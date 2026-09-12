"""
nicotin.network.session
~~~~~~~~~~~~~~~~~~~~~~~~

Low-level transport for Rubika's official **Bot API** (the same kind
of platform-provided, token-authenticated REST API Telegram bots use
— not the reverse-engineered user/session API). The bot token lives
in the URL path, every request/response body is plain JSON with no
extra encryption layer, so this module is intentionally much thinner
than a user-session client would need to be.
"""

from __future__ import annotations

from typing import Any

import httpx

from ..errors import RPCError, ConnectionError_, FloodWait, RequestTimeout

DEFAULT_BASE_URL = "https://botapi.rubika.ir/v3"
DEFAULT_TIMEOUT = 15


class Session:
    """
    One HTTPS session against Rubika's Bot API for a single bot token.

    :param bot_token: the token you got from **Rubika Bot** (``@rubika_bot``)
        when you created your bot — the only credential a bot needs.
    :param base_url: override the API base URL if Rubika ever changes it.
    """

    def __init__(
        self,
        bot_token: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.bot_token = bot_token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._http = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        await self._http.aclose()

    def _url_for(self, method: str) -> str:
        return f"{self.base_url}/{self.bot_token}/{method}"

    async def invoke(self, method: str, data: dict[str, Any] | None = None) -> dict:
        """
        Call one Bot API ``method`` with a plain-JSON ``data`` body,
        returning the ``data`` object from a successful response.

        Raises :class:`~nicotin.errors.RPCError` / :class:`~nicotin.errors.FloodWait`
        on failure, matching how Pyrogram surfaces RPC errors from ``invoke()``.
        """
        try:
            response = await self._http.post(self._url_for(method), json=data or {})
        except httpx.TimeoutException as e:
            raise RequestTimeout(f"'{method}' timed out after {self.timeout}s") from e
        except httpx.HTTPError as e:
            raise ConnectionError_(str(e)) from e

        try:
            body = response.json()
        except ValueError as e:
            raise RPCError("INVALID_RESPONSE", "Server returned non-JSON body") from e

        status = body.get("status", "ERROR" if response.status_code >= 400 else "OK")

        if status == "OK":
            return body.get("data", {})

        if status in ("FLOOD_WAIT", "TOO_MANY_REQUESTS"):
            raise FloodWait(int(body.get("retry_after", 5)))

        raise RPCError(status, body.get("message") or body.get("status_det"))

    async def upload_file(self, upload_url: str, file_path: str) -> dict:
        """POST a local file's bytes to an upload URL returned by ``requestSendFile``."""
        with open(file_path, "rb") as f:
            try:
                response = await self._http.post(upload_url, files={"file": f})
            except httpx.TimeoutException as e:
                raise RequestTimeout(f"file upload timed out after {self.timeout}s") from e
            except httpx.HTTPError as e:
                raise ConnectionError_(str(e)) from e
        try:
            return response.json()
        except ValueError as e:
            raise RPCError("INVALID_RESPONSE", "Upload server returned non-JSON body") from e
