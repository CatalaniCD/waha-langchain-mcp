"""Print the tools advertised by the waha-mcp server and call waha_status."""

from __future__ import annotations

import asyncio
import json

from common import load_waha_tools


async def main() -> None:
    tools = await load_waha_tools()
    for tool in tools:
        print(f"- {tool.name}: {(tool.description or '').splitlines()[0]}")
    status = next(tool for tool in tools if tool.name == "waha_status")
    print(json.dumps(await status.ainvoke({}), indent=2))


if __name__ == "__main__":
    asyncio.run(main())
