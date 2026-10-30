# 0001 — Expose WAHA through a Python stdio MCP server

## Context

A local WAHA instance (WhatsApp HTTP API) runs at `http://localhost:3000`.
LangChain ReAct and deep agents need WhatsApp capabilities as tools. The
agents are Python, and the MCP server must not expose the WAHA API key to the
model or to prompt text.

## Decision

- Build a **Python** MCP server with the official `mcp` SDK (`FastMCP`).
- Use **stdio** transport. The LangChain process spawns the server; no port is
  opened and the API key stays in the server process environment.
- Isolate all WAHA HTTP concerns in a single `WahaClient` wrapper. MCP tools
  are thin typed adapters over that client.
- LangChain integrations consume tools via `langchain-mcp-adapters`; the same
  tool list is reused by both `create_react_agent` and `create_deep_agent`.

## Consequences

- Easier: any MCP host (Claude Desktop, Cursor, LangChain) can reuse the server.
- Easier: WAHA API changes are contained in `client.py`.
- Harder: stdio is 1:1 per agent process; a shared HTTP transport would require
  an extra port and auth. Inbound WhatsApp events are not pushed over MCP —
  use WAHA webhooks for that (explicitly out of scope).
- Rejected: TypeScript server (extra runtime, agents are Python) and a custom
  LangChain Tool wrapper per endpoint (duplicates the MCP contract).
