"""LangChain ReAct agent wired to the WAHA MCP server.

Run:
    uv run python examples/react_agent.py "List my recent WhatsApp chats"
"""

from __future__ import annotations

import asyncio

from langchain.agents import create_agent

from common import load_model, load_waha_tools, prompt_from_argv

SYSTEM_PROMPT = (
    "You are a WhatsApp assistant. Use the waha_* tools to inspect sessions, "
    "read chats, and send messages only when the user explicitly asks you to. "
    "Never invent chat IDs: get them from waha_list_chats or "
    "waha_check_number_exists."
)


async def main(prompt: str) -> None:
    tools = await load_waha_tools()
    agent = create_agent(load_model(), tools, system_prompt=SYSTEM_PROMPT)
    result = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]})
    print(result["messages"][-1].text())


if __name__ == "__main__":
    asyncio.run(
        main(
            prompt_from_argv(
                "Check WAHA connectivity, list my sessions, and show the 5 most "
                "recent chats of the first working session."
            )
        )
    )
