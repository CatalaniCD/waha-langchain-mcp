"""MCP server for WAHA (WhatsApp HTTP API)."""

from .client import WahaClient, WahaError

__all__ = ["WahaClient", "WahaError"]
