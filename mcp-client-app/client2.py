import asyncio
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI


PROJECT_DIR = Path(__file__).resolve().parent
MANIM_OUTPUT_DIR = PROJECT_DIR / "manim_outputs"
load_dotenv()

SERVERS = {
    "math": {
        "transport": "stdio",
        "command": sys.executable,
        "args": [str(PROJECT_DIR / "main.py")],
    }
}

if os.getenv("INCLUDE_REMOTE_MCP") == "1":
    SERVERS["expense"] = {
        "transport": "streamable_http",
        "url": "https://deepak-bishnoi-mcp.fastmcp.app/mcp",
    }

SYSTEM_PROMPT = (
    "You have access to tools. Use brave_search for current events or web questions. "
    "For animation requests, generate complete Manim Community Python code and call "
    "render_manim_code with scene_code and the matching scene_name class. "
    "When you choose to call a tool, do not narrate status updates. "
    "After tools run, return only a concise final answer."
)


def run_async(coro):
    return asyncio.run(coro)


def can_import_manim():
    try:
        __import__("manim")
    except ImportError:
        return False
    return True


@tool
def brave_search(query: str, params: dict | None = None) -> str:
    """Search the web for current information."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Web search is not configured because TAVILY_API_KEY is missing."

    max_results = 5
    if params and isinstance(params.get("max_results"), int):
        max_results = max(1, min(params["max_results"], 10))

    response = requests.post(
        "https://api.tavily.com/search",
        headers={"Authorization": f"Bearer {api_key}"},
        json={
            "query": query,
            "search_depth": "basic",
            "max_results": max_results,
            "include_answer": True,
        },
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()

    lines = []
    if data.get("answer"):
        lines.append(f"Answer: {data['answer']}")

    for item in data.get("results", []):
        title = item.get("title") or "Untitled"
        url = item.get("url") or ""
        content = item.get("content") or ""
        lines.append(f"- {title}\n  URL: {url}\n  Summary: {content}")

    return "\n".join(lines) if lines else "No search results found."


@tool
def render_manim_code(scene_code: str, scene_name: str = "GeneratedScene") -> str:
    """Render a Manim Community animation from Python scene code."""
    if not shutil.which("manim") and not can_import_manim():
        return (
            "Manim is not installed. Run "
            "`uv pip install --python .\\.venv\\Scripts\\python.exe manim`, "
            "then restart Streamlit."
        )

    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", scene_name):
        return "Invalid scene_name. Use a valid Python class name like GeneratedScene."

    MANIM_OUTPUT_DIR.mkdir(exist_ok=True)
    scene_file = MANIM_OUTPUT_DIR / "generated_scene.py"
    scene_file.write_text(scene_code, encoding="utf-8")

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "manim",
                "-ql",
                str(scene_file),
                scene_name,
                "--media_dir",
                str(MANIM_OUTPUT_DIR / "media"),
            ],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return "Manim render timed out after 180 seconds."
    if result.returncode != 0:
        return f"Manim render failed.\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"

    video_paths = sorted(
        (MANIM_OUTPUT_DIR / "media").rglob("*.mp4"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not video_paths:
        return f"Manim finished, but no MP4 was found.\nSTDOUT:\n{result.stdout}"

    return f"Rendered video: {video_paths[0]}"


def build_llm():
    provider = os.getenv("LLM_PROVIDER", "groq").strip().lower()

    if provider == "openai":
        if not os.getenv("OPENAI_API_KEY"):
            st.error("OPENAI_API_KEY is missing from .env.")
            st.stop()
        return ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-5"))

    if provider == "groq":
        if not os.getenv("GROQ_API_KEY"):
            st.error("GROQ_API_KEY is missing from .env.")
            st.stop()
        return ChatGroq(model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))

    st.error("LLM_PROVIDER must be either 'groq' or 'openai'.")
    st.stop()


def show_llm_error(exc):
    message = str(exc)
    if "insufficient_quota" in message:
        st.error(
            "OpenAI rejected the request because the account has no available quota. "
            "This app now defaults to Groq; set LLM_PROVIDER=groq in .env or add billing/quota "
            "to the OpenAI account before using LLM_PROVIDER=openai."
        )
    else:
        st.error(f"LLM request failed: {exc}")


def invoke_llm(llm_with_tools, messages):
    try:
        return run_async(llm_with_tools.ainvoke(messages))
    except Exception as exc:
        show_llm_error(exc)
        with st.expander("Technical details"):
            st.code(str(exc))
        return None


st.set_page_config(page_title="MCP Chat", layout="centered")
st.title("MCP Chat")

st.sidebar.caption(f"Provider: {os.getenv('LLM_PROVIDER', 'groq')}")

if "initialized" not in st.session_state:
    st.session_state.llm = build_llm()
    st.session_state.client = MultiServerMCPClient(SERVERS)

    mcp_tools = [
        tool
        for tool in run_async(st.session_state.client.get_tools())
        if tool.name != "render_manim_code"
    ]
    tools = [*mcp_tools, brave_search, render_manim_code]
    st.session_state.tools = tools
    st.session_state.tool_by_name = {tool.name: tool for tool in tools}
    st.session_state.llm_with_tools = st.session_state.llm.bind_tools(tools)
    st.session_state.history = [SystemMessage(content=SYSTEM_PROMPT)]
    st.session_state.initialized = True

st.sidebar.caption("Tools: " + ", ".join(sorted(st.session_state.tool_by_name)))

for msg in st.session_state.history:
    if isinstance(msg, HumanMessage):
        with st.chat_message("user"):
            st.markdown(msg.content)
    elif isinstance(msg, AIMessage):
        if getattr(msg, "tool_calls", None):
            continue
        with st.chat_message("assistant"):
            st.markdown(msg.content)

user_text = st.chat_input("Type a message...")
if user_text:
    with st.chat_message("user"):
        st.markdown(user_text)
    st.session_state.history.append(HumanMessage(content=user_text))

    first = invoke_llm(st.session_state.llm_with_tools, st.session_state.history)
    if first is None:
        st.stop()

    tool_calls = getattr(first, "tool_calls", None)

    if not tool_calls:
        with st.chat_message("assistant"):
            st.markdown(first.content or "")
        st.session_state.history.append(first)
    else:
        st.session_state.history.append(first)

        tool_messages = []
        for tool_call in tool_calls:
            name = tool_call["name"]
            args = tool_call.get("args") or {}
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except json.JSONDecodeError:
                    pass

            tool = st.session_state.tool_by_name.get(name)
            if tool is None:
                result = f"Unknown tool requested: {name}"
            else:
                try:
                    result = run_async(tool.ainvoke(args))
                except Exception as exc:
                    result = f"Tool {name} failed: {exc}"

            tool_messages.append(
                ToolMessage(tool_call_id=tool_call["id"], content=json.dumps(result))
            )

        st.session_state.history.extend(tool_messages)

        final = invoke_llm(st.session_state.llm_with_tools, st.session_state.history)
        if final is None:
            st.stop()

        with st.chat_message("assistant"):
            st.markdown(final.content or "")
        st.session_state.history.append(AIMessage(content=final.content or ""))
