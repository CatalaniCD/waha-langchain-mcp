"""Shared MCP + model setup for the LangChain examples."""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def load_model() -> BaseChatModel:
    model = os.getenv("AGENT_MODEL", "openrouter:openai/gpt-4o-mini")
    return init_chat_model(model)


async def load_waha_tools() -> list[BaseTool]:
    """Start the waha-mcp server over stdio and return its tools to LangChain."""
    client = MultiServerMCPClient(
        {
            "waha": {
                "command": sys.executable,
                "args": ["-m", "waha_mcp"],
                "transport": "stdio",
                "env": {
                    **os.environ,
                    "WAHA_BASE_URL": os.getenv(
                        "WAHA_BASE_URL", "http://localhost:3000"
                    ),
                    "WAHA_API_KEY": os.getenv("WAHA_API_KEY", ""),
                },
            }
        }
    )
    return await client.get_tools()


def prompt_from_argv(default: str) -> str:
    return " ".join(sys.argv[1:]).strip() or default
