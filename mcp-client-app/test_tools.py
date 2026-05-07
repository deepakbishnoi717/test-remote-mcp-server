import asyncio
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient


PROJECT_DIR = Path(__file__).resolve().parent


async def test_math_tools():
    client = MultiServerMCPClient(
        {
            "math": {
                "transport": "stdio",
                "command": sys.executable,
                "args": [str(PROJECT_DIR / "main.py")],
            }
        }
    )
    tools = await client.get_tools()
    by_name = {tool.name: tool for tool in tools}

    print("MCP tools:", ", ".join(sorted(by_name)))
    checks = {
        "add": ({"a": 2, "b": 3}, 5.0),
        "subtract": ({"a": 10, "b": 4}, 6.0),
        "multiply": ({"a": 6, "b": 7}, 42.0),
        "divide": ({"a": 20, "b": 5}, 4.0),
    }

    for name, (args, expected) in checks.items():
        result = await by_name[name].ainvoke(args)
        status = "ok" if result == expected else f"expected {expected}"
        print(f"{name}: {result} ({status})")



def test_search_tool():
    api_key = os.getenv("TAVILY_API_KEY")
    print("TAVILY_API_KEY:", "present" if api_key else "missing")
    if not api_key:
        return

    response = requests.post(
        "https://api.tavily.com/search",
        headers={"Authorization": f"Bearer {api_key}"},
        json={"query": "test search", "search_depth": "basic", "max_results": 1},
        timeout=20,
    )
    print("brave_search backend:", response.status_code)
    response.raise_for_status()


async def main():
    load_dotenv()
    await test_math_tools()
    test_search_tool()


if __name__ == "__main__":
    asyncio.run(main())
