# MCP Client App

Streamlit chat app with local MCP math tools, Tavily-backed web search, and a Manim rendering tool.

## Setup

1. Create `.env` from `.env.example`.
2. Install dependencies into the project virtual environment.
3. Start the app:

```bat
run_app.bat
```

Open `http://localhost:8501`.

## Tool Test

```bat
.\.venv\Scripts\python.exe -B test_tools.py
```

## Manim Test

```bat
.\.venv\Scripts\python.exe -B -m manim -ql manim_test_scene.py GeneratedScene --media_dir manim_outputs\direct_media
```
