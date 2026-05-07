# Remote MCP Server and Client Showcase

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-FastMCP-111827)](https://github.com/jlowin/fastmcp)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B)](https://streamlit.io/)
[![Manim](https://img.shields.io/badge/Animation-Manim-0E7C7B)](https://www.manim.community/)

A practical Model Context Protocol workspace with two connected parts:

- A **remote-ready FastMCP expense server** for structured expense tracking.
- A **Streamlit MCP client app** with local math tools, web search, Groq/OpenAI LLM support, and Manim animation rendering.

This repo is designed as a compact reference for building MCP tools, exposing them through a server, and consuming them from a chat UI.

## What This Shows

| Area | What is included |
| --- | --- |
| MCP server | FastMCP tools for expense management with SQLite persistence |
| MCP client | Streamlit chat app using `langchain-mcp-adapters` |
| Tool calling | Math tools, Tavily-backed search, and Manim video rendering |
| LLM providers | Groq by default, OpenAI available through config |
| Local testing | Smoke tests for MCP tools, search backend, and Manim rendering |

## Repository Structure

```text
test-remote-mcp-server/
|-- main.py                  # FastMCP expense server
|-- proxy.py                 # Proxy entrypoint for remote access
|-- categories.json          # Expense category definitions
|-- pyproject.toml           # Server dependencies
|-- uv.lock                  # Server lockfile
|-- mcp-client-app/          # Streamlit MCP client showcase
|   |-- client2.py           # Main web app
|   |-- main.py              # Local math MCP server
|   |-- test_tools.py        # Tool smoke tests
|   |-- manim_test_scene.py  # Direct Manim render test
|   |-- .env.example         # Safe environment template
|   `-- README.md            # Client app guide
`-- README.md
```

## FastMCP Expense Server

The root server exposes expense tracking tools backed by SQLite. It is useful for testing remote MCP tool workflows and structured tool arguments.

### Server Setup

```bash
git clone https://github.com/deepakbishnoi717/test-remote-mcp-server.git
cd test-remote-mcp-server
uv sync
```

Run the local server:

```bash
uv run python main.py
```

Run the proxy entrypoint:

```bash
uv run python proxy.py
```

### Expense Tool Example

Use natural language from an MCP-compatible client:

```text
Add an expense for 450 INR in Food, subcategory Lunch, with note "team meal".
```

## Streamlit MCP Client App

The client app lives in [`mcp-client-app/`](./mcp-client-app). It demonstrates a chat UI that can call tools from both an MCP server and direct LangChain tools.

Highlights:

- Local MCP math server: `add`, `subtract`, `multiply`, `divide`
- Tavily-backed web search tool exposed as `brave_search`
- Manim renderer exposed as `render_manim_code`
- Groq model support by default
- OpenAI fallback through `.env`
- Windows-friendly launcher: `run_app.bat`

Start the client:

```bat
cd mcp-client-app
copy .env.example .env
run_app.bat
```

Open:

```text
http://localhost:8501
```

## Demo Prompts

Try these in the Streamlit app:

```text
Use the math tool to multiply 12 by 8, then subtract 10.
```

```text
Search the web for the latest Model Context Protocol updates and summarize them.
```

```text
Use render_manim_code to create a Manim animation of a blue circle transforming into a green square. Return the rendered video path.
```

## Validation

From the client folder:

```bat
.\.venv\Scripts\python.exe -B test_tools.py
```

Direct Manim render test:

```bat
.\.venv\Scripts\python.exe -B -m manim -ql manim_test_scene.py GeneratedScene --media_dir manim_outputs\direct_media
```

Expected Manim output:

```text
manim_outputs\direct_media\videos\manim_test_scene\480p15\GeneratedScene.mp4
```

## Environment Variables

The client app uses `.env.example` as a safe template:

| Variable | Purpose |
| --- | --- |
| `GROQ_API_KEY` | Required for Groq chat models |
| `TAVILY_API_KEY` | Required for web search |
| `OPENAI_API_KEY` | Optional OpenAI provider |
| `LLM_PROVIDER` | `groq` or `openai` |
| `GROQ_MODEL` | Default Groq model |
| `OPENAI_MODEL` | Default OpenAI model |

Never commit a real `.env` file.

## Tech Stack

- FastMCP and MCP
- LangChain tool binding
- Streamlit
- Groq and OpenAI chat providers
- Tavily Search API
- Manim Community
- SQLite
- uv

## Notes

- The root server and the client app are intentionally separated so each can be studied or deployed independently.
- Generated videos and local virtual environments are ignored by Git.
- The client defaults to Groq to avoid OpenAI quota errors during local testing.
