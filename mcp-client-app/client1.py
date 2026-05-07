import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.messages import ToolMessage
from langchain_groq import ChatGroq
from langchain_mcp_adapters.client import MultiServerMCPClient


PROJECT_DIR = Path(__file__).resolve().parent

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


async def run_local_demo(named_tools):
    add_tool = named_tools.get("add")
    if add_tool is None:
        print("The local math MCP server did not expose an 'add' tool.")
        return

    result = await add_tool.ainvoke({"a": 2, "b": 3})
    print("add(2, 3) =", result)


async def run_llm_demo(tools, named_tools):
    llm = ChatGroq(model="llama-3.3-70b-versatile")
    llm_with_tools = llm.bind_tools(tools)

    prompt = "Use the available math tool to add 2 and 3."
    response = await llm_with_tools.ainvoke(prompt)

    if not getattr(response, "tool_calls", None):
        print("\nLLM Reply:", response.content)
        return

    tool_messages = []
    for tool_call in response.tool_calls:
        selected_tool = tool_call["name"]
        selected_tool_args = tool_call.get("args") or {}
        selected_tool_id = tool_call["id"]

        result = await named_tools[selected_tool].ainvoke(selected_tool_args)
        tool_messages.append(
            ToolMessage(
                tool_call_id=selected_tool_id,
                content=json.dumps(result),
            )
        )

    final_response = await llm_with_tools.ainvoke([prompt, response, *tool_messages])
    print(f"Final response: {final_response.content}")


async def main():
    load_dotenv()

    client = MultiServerMCPClient(SERVERS)
    tools = await client.get_tools()
    named_tools = {tool.name: tool for tool in tools}

    print("Available tools:", ", ".join(sorted(named_tools)))
    await run_local_demo(named_tools)

    if os.getenv("RUN_LLM_DEMO") == "1":
        await run_llm_demo(tools, named_tools)


if __name__ == "__main__":
    asyncio.run(main())
