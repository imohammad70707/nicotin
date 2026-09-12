from __future__ import annotations

from .object import Object


class User(Object):
    """
    A Rubika user, shaped like Pyrogram's ``User``.

    :param id: the user's ``object_guid`` (e.g. ``u0AbC123...``).
    :param first_name: the user's first name.
    :param last_name: the user's last name, if any.
    :param username: the user's public ``@username``, if set.
    :param phone: the user's phone number, only present for the logged-in account.
    :param is_verified: whether the account carries Rubika's verified badge.
    :param is_bot: whether this "user" is actually a bot account.
    :param is_deleted: whether the account has been deleted.
    """

    def __init__(
        self,
        *,
        client=None,
        id: str,
        first_name: str,
        last_name: str | None = None,
        username: str | None = None,
        phone: str | None = None,
        is_verified: bool = False,
        is_bot: bool = False,
        is_deleted: bool = False,
    ):
        self._client = client
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.phone = phone
        self.is_verified = is_verified
        self.is_bot = is_bot
        self.is_deleted = is_deleted

    @property
    def full_name(self) -> str:
        return " ".join(filter(None, (self.first_name, self.last_name)))

    @property
    def mention(self) -> str:
        """Markdown mention of this user, e.g. for use in ``send_message(..., parse_mode=...)``."""
        return f"[{self.full_name}](rubika://user?id={self.id})"

    async def send_message(self, text: str, **kwargs):
        """Shortcut for ``client.send_message(user.id, text)``."""
        return await self._client.send_message(self.id, text, **kwargs)

    @classmethod
    def _parse(cls, client, data: dict) -> "User":
        # Covers both a regular user object and the Bot API's "getMe"
        # bot object (bot_id / bot_title instead of user_guid / first_name).
        return cls(
            client=client,
            id=data.get("user_guid") or data.get("bot_id") or data.get("id", ""),
            first_name=data.get("first_name") or data.get("bot_title", ""),
            last_name=data.get("last_name"),
            username=data.get("username"),
            phone=data.get("phone"),
            is_verified=data.get("is_verified", False),
            is_bot=data.get("is_bot", "bot_id" in data),
            is_deleted=data.get("is_deleted", False),
        )
