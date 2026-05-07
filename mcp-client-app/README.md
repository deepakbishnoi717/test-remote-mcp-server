# MCP Client App

A Streamlit chat interface that connects local MCP tools with LLM tool calling. It is built to demonstrate a practical client-side MCP workflow: local tools, web search, and generated animation output from one chat surface.

## Features

| Feature | Tool |
| --- | --- |
| Math operations | `add`, `subtract`, `multiply`, `divide` |
| Web search | `brave_search` backed by Tavily |
| Animation rendering | `render_manim_code` backed by Manim Community |
| LLM provider | Groq by default, OpenAI optional |
| UI | Streamlit chat app |

## Setup

Create your environment file:

```bat
copy .env.example .env
```

Fill in the required keys:

```text
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
LLM_PROVIDER=groq
```

Install dependencies using your preferred workflow. With uv:

```bat
uv sync
```

Start the app:

```bat
run_app.bat
```

Open:

```text
http://localhost:8501
```

## Demo Prompts

Math tool:

```text
Use the math tools to multiply 25 by 4 and then divide the result by 5.
```

Web search:

```text
Use brave_search to find recent MCP news and summarize the top results.
```

Manim render:

```text
Use render_manim_code to create a Manim animation of a blue circle transforming into a green square. Return the rendered video path.
```

## Tool Smoke Test

Run:

```bat
.\.venv\Scripts\python.exe -B test_tools.py
```

Expected checks:

- MCP math tools are listed.
- `add`, `subtract`, `multiply`, and `divide` return correct values.
- `TAVILY_API_KEY` is present.
- Search backend returns HTTP `200`.

## Manim Test

Check Manim is installed:

```bat
.\.venv\Scripts\python.exe -B -m manim --version
```

Render the sample scene:

```bat
.\.venv\Scripts\python.exe -B -m manim -ql manim_test_scene.py GeneratedScene --media_dir manim_outputs\direct_media
```

Expected output:

```text
manim_outputs\direct_media\videos\manim_test_scene\480p15\GeneratedScene.mp4
```

## Important Notes

- Use `run_app.bat` or `.venv\Scripts\python.exe -m streamlit run client2.py`.
- Do not start the app with plain `python -m streamlit` unless that Python is your project virtual environment.
- Real `.env` files, virtual environments, and generated videos should stay out of Git.
