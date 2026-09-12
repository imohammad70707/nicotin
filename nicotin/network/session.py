"""
nicotin.network.session
~~~~~~~~~~~~~~~~~~~~~~~~

Low-level transport: builds the JSON envelope Rubika's REST API
expects, sends it over HTTPS with ``httpx``, and unwraps the response
— comparable to Pyrogram's MTProto ``Session`` class, but far simpler
since Rubika speaks plain HTTPS/JSON rather than a binary protocol.

Rubika's real production clients additionally AES-encrypt the
``data_enc`` field of every request/response using a key derived from
login; that layer is intentionally kept out of this skeleton so it can
be swapped in (e.g. via ``pycryptodome``) without touching anything
above this module — see :meth:`Session.encrypt` / :meth:`Session.decrypt`.
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from typing import Any

import httpx

from ..errors import RPCError, ConnectionError_, FloodWait

DEFAULT_API_URL = "https://messengerg2c1.iranlms.ir/"
DEFAULT_TIMEOUT = 15


class Session:
    """
    One HTTPS session against a Rubika API endpoint.

    :param auth: the account's auth key, obtained once via login/OTP.
    :param platform: reported client platform, e.g. ``"web"`` or ``"android"``.
    :param api_url: base API URL; override for a different DC.
    """

    def __init__(
        self,
        auth: str,
        *,
        platform: str = "web",
        api_url: str = DEFAULT_API_URL,
        timeout: int = DEFAULT_TIMEOUT,
    ):
        self.auth = auth
        self.platform = platform
        self.api_url = api_url
        self.timeout = timeout
        self._http = httpx.AsyncClient(timeout=timeout)

    async def close(self):
        await self._http.aclose()

    # ------------------------------------------------------------------
    # Encryption hooks — plug real AES-256-CBC (keyed off `auth`) in here.
    # Left as no-ops so the rest of the library is fully testable/offline.
    # ------------------------------------------------------------------

    def encrypt(self, data: dict) -> str:
        return json.dumps(data)

    def decrypt(self, data_enc: str) -> dict:
        return json.loads(data_enc)

    async def invoke(self, method: str, data: dict[str, Any]) -> dict:
        """
        Call one Rubika API ``method`` with ``data``, returning the
        already-unwrapped ``data`` object from a successful response.

        Raises :class:`~nicotin.errors.RPCError` / :class:`~nicotin.errors.FloodWait`
        on failure, matching how Pyrogram surfaces RPC errors from ``invoke()``.
        """
        payload = {
            "api_version": "6",
            "auth": self.auth,
            "client": {
                "app_name": "Main",
                "app_version": "4.4.1",
                "platform": self.platform,
                "package": "app.rbmain.a",
                "lang_code": "fa",
            },
            "data_enc": self.encrypt({"method": method, "input": data, "client": {}}),
            "method": method,
            "tmp_session": uuid.uuid4().hex,
        }

        try:
            response = await self._http.post(self.api_url, json=payload)
        except httpx.HTTPError as e:
            raise ConnectionError_(str(e)) from e

        try:
            body = response.json()
        except ValueError as e:
            raise RPCError("INVALID_RESPONSE", "Server returned non-JSON body") from e

        status = body.get("status", "ERROR")

        if status == "OK":
            return self.decrypt(body.get("data_enc", "{}"))

        if status == "FLOOD_WAIT":
            raise FloodWait(int(body.get("status_det", 5)))

        raise RPCError(status, body.get("status_det"))
