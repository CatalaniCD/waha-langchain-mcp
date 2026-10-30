"""Deep agent (deepagents) wired to the WAHA MCP server.

Run:
    uv run python examples/deep_agent.py "Summarize my unread WhatsApp chats"
"""

from __future__ import annotations

import asyncio

from deepagents import create_deep_agent

from common import load_model, load_waha_tools, prompt_from_argv

SYSTEM_PROMPT = (
    "You are a WhatsApp operations assistant. Prefer the waha_* MCP tools over "
    "guessing. Sending a message is an irreversible side effect: only do it "
    "when the user asks explicitly. For broad questions, plan first, then read "
    "chats and messages before answering."
)


async def main(prompt: str) -> None:
    tools = await load_waha_tools()
    agent = create_deep_agent(
        model=load_model(),
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
    )
    result = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]})
    print(result["messages"][-1].text())


if __name__ == "__main__":
    asyncio.run(
        main(
            prompt_from_argv(
                "List my sessions and the 5 most recent chats of the first "
                "working session. Do not send anything."
            )
        )
    )
