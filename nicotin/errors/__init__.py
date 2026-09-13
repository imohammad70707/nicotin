"""
nicotin.errors
~~~~~~~~~~~~~~

Exception hierarchy modeled after Pyrogram's ``errors`` package: one
root exception, with specific, catchable subclasses for the situations
that come up most often when talking to Rubika's API.
"""


class NicotinError(Exception):
    """Base class for every exception raised by NICOTIN."""


class RPCError(NicotinError):
    """
    Raised when the Rubika API server itself returns a non-OK status.

    :param status: the raw ``status`` field returned by the API
        (e.g. ``"INVALID_INPUT"``, ``"NOT_REGISTERED"``).
    :param message: a human readable description, if the server sent one.
    """

    def __init__(self, status: str, message: str | None = None):
        self.status = status
        self.message = message or status
        super().__init__(f"[{status}] {self.message}")


class AuthError(NicotinError):
    """Raised when the bot token is missing, malformed, or rejected by Rubika."""


class FloodWait(NicotinError):
    """
    Raised when Rubika asks the client to slow down.

    :param value: number of seconds the client should wait before retrying.
    """

    def __init__(self, value: int):
        self.value = value
        super().__init__(f"A wait of {value} seconds is required")


class ConnectionError_(NicotinError):
    """Raised when NICOTIN cannot reach any Rubika API endpoint."""


class RequestTimeout(NicotinError):
    """Raised when a request to the Rubika API times out."""


class BadRequest(RPCError):
    """The request was malformed or missing required fields."""


class Unauthorized(RPCError):
    """The current session/auth is no longer valid."""


class NotFound(RPCError):
    """The requested chat, message or object_guid does not exist."""


__all__ = [
    "NicotinError",
    "RPCError",
    "AuthError",
    "FloodWait",
    "ConnectionError_",
    "RequestTimeout",
    "BadRequest",
    "Unauthorized",
    "NotFound",
]
