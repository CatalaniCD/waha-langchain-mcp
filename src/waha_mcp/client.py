"""Async HTTP client for the WAHA REST API."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import quote

import httpx
from dotenv import load_dotenv


class WahaError(RuntimeError):
    """Raised when WAHA returns an error or cannot be reached."""


@dataclass(slots=True)
class WahaClient:
    base_url: str = "http://localhost:3000"
    api_key: str | None = None
    timeout: float = 30.0
    _http: httpx.AsyncClient = field(init=False, repr=False)

    def __post_init__(self) -> None:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["X-Api-Key"] = self.api_key
        self._http = httpx.AsyncClient(
            base_url=self.base_url.rstrip("/"),
            headers=headers,
            timeout=self.timeout,
        )

    @classmethod
    def from_env(cls) -> WahaClient:
        load_dotenv()
        return cls(
            base_url=os.getenv("WAHA_BASE_URL", "http://localhost:3000"),
            api_key=os.getenv("WAHA_API_KEY") or None,
            timeout=float(os.getenv("WAHA_TIMEOUT", "30")),
        )

    async def __aenter__(self) -> WahaClient:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        await self._http.aclose()

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            response = await self._http.request(method, path, **kwargs)
        except httpx.HTTPError as exc:
            raise WahaError(f"WAHA request failed ({method} {path}): {exc}") from exc

        if response.status_code >= 400:
            raise WahaError(
                f"WAHA {response.status_code} ({method} {path}): {response.text[:1000]}"
            )
        if response.status_code == 204 or not response.content:
            return None
        if "application/json" not in response.headers.get("content-type", ""):
            return response.content
        return response.json()

    @staticmethod
    def _session(session: str) -> str:
        return quote(session, safe="")

    @staticmethod
    def _chat(chat_id: str) -> str:
        return quote(chat_id, safe="")

    async def version(self) -> dict[str, Any]:
        return await self._request("GET", "/api/version")

    async def server_status(self) -> dict[str, Any]:
        return await self._request("GET", "/api/server/status")

    async def list_sessions(self, all: bool = False) -> list[dict[str, Any]]:
        return await self._request("GET", "/api/sessions", params={"all": str(all).lower()})

    async def get_session(self, session: str) -> dict[str, Any]:
        return await self._request("GET", f"/api/sessions/{self._session(session)}")

    async def get_me(self, session: str) -> dict[str, Any]:
        return await self._request(
            "GET", f"/api/sessions/{self._session(session)}/me"
        )

    async def create_session(self, name: str, start: bool = True) -> dict[str, Any]:
        return await self._request(
            "POST", "/api/sessions", json={"name": name, "start": start}
        )

    async def start_session(self, session: str) -> dict[str, Any]:
        return await self._request(
            "POST", f"/api/sessions/{self._session(session)}/start"
        )

    async def stop_session(self, session: str) -> dict[str, Any]:
        return await self._request(
            "POST", f"/api/sessions/{self._session(session)}/stop"
        )

    async def list_chats(
        self, session: str, limit: int = 20, offset: int = 0
    ) -> list[dict[str, Any]]:
        return await self._request(
            "GET",
            f"/api/{self._session(session)}/chats",
            params={"limit": limit, "offset": offset},
        )

    async def get_chat(self, session: str, chat_id: str) -> dict[str, Any]:
        return await self._request(
            "GET",
            f"/api/{self._session(session)}/chats/{self._chat(chat_id)}",
        )

    async def get_messages(
        self,
        session: str,
        chat_id: str,
        limit: int = 20,
        offset: int = 0,
        download_media: bool = False,
    ) -> list[dict[str, Any]]:
        return await self._request(
            "GET",
            f"/api/{self._session(session)}/chats/{self._chat(chat_id)}/messages",
            params={
                "limit": limit,
                "offset": offset,
                "downloadMedia": str(download_media).lower(),
            },
        )

    async def get_message(
        self, session: str, chat_id: str, message_id: str
    ) -> dict[str, Any]:
        return await self._request(
            "GET",
            f"/api/{self._session(session)}/chats/{self._chat(chat_id)}"
            f"/messages/{self._chat(message_id)}",
        )

    async def send_text(
        self,
        session: str,
        chat_id: str,
        text: str,
        reply_to: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "session": session,
            "chatId": chat_id,
            "text": text,
        }
        if reply_to:
            payload["reply_to"] = reply_to
        return await self._request("POST", "/api/sendText", json=payload)

    async def send_image(
        self,
        session: str,
        chat_id: str,
        file: dict[str, Any],
        caption: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "session": session,
            "chatId": chat_id,
            "file": file,
        }
        if caption:
            payload["caption"] = caption
        return await self._request("POST", "/api/sendImage", json=payload)

    async def send_file(
        self,
        session: str,
        chat_id: str,
        file: dict[str, Any],
        caption: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "session": session,
            "chatId": chat_id,
            "file": file,
        }
        if caption:
            payload["caption"] = caption
        return await self._request("POST", "/api/sendFile", json=payload)

    async def mark_chat_read(self, session: str, chat_id: str) -> Any:
        return await self._request(
            "POST",
            f"/api/{self._session(session)}/chats/{self._chat(chat_id)}/messages/read",
            json={},
        )

    async def start_typing(self, session: str, chat_id: str) -> Any:
        return await self._request(
            "POST",
            "/api/startTyping",
            json={"session": session, "chatId": chat_id},
        )

    async def stop_typing(self, session: str, chat_id: str) -> Any:
        return await self._request(
            "POST",
            "/api/stopTyping",
            json={"session": session, "chatId": chat_id},
        )

    async def check_number_exists(self, session: str, phone: str) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/api/contacts/check-exists",
            params={"session": session, "phone": phone},
        )

    async def profile_picture(self, session: str, contact_id: str) -> dict[str, Any]:
        return await self._request(
            "GET",
            "/api/contacts/profile-picture",
            params={"session": session, "contactId": contact_id},
        )

    async def screenshot(self, session: str) -> bytes:
        return await self._request("GET", "/api/screenshot", params={"session": session})
