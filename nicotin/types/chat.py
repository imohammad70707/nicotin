from __future__ import annotations

from .object import Object
from ..enums import ChatType


class Chat(Object):
    """
    A chat (private, group or channel), shaped like Pyrogram's ``Chat``.

    :param id: the chat's ``object_guid``.
    :param type: a :class:`~nicotin.enums.ChatType` describing the guid's kind.
    :param title: the group/channel title (``None`` for private chats).
    :param first_name: for private chats, the other user's first name.
    :param last_name: for private chats, the other user's last name.
    :param username: the chat's public ``@username``, if set.
    :param members_count: number of members, for groups/channels.
    :param description: the group/channel bio, if set.
    """

    def __init__(
        self,
        *,
        client=None,
        id: str,
        type: ChatType,
        title: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        username: str | None = None,
        members_count: int | None = None,
        description: str | None = None,
    ):
        self._client = client
        self.id = id
        self.type = type
        self.title = title
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.members_count = members_count
        self.description = description

    async def send_message(self, text: str, **kwargs):
        return await self._client.send_message(self.id, text, **kwargs)

    async def ban_member(self, user_id: str):
        return await self._client.ban_chat_member(self.id, user_id)

    async def unban_member(self, user_id: str):
        return await self._client.unban_chat_member(self.id, user_id)

    async def leave(self):
        return await self._client.leave_chat(self.id)

    @classmethod
    def _parse(cls, client, data: dict) -> "Chat":
        guid = data.get("object_guid") or data.get("chat_id") or data.get("id", "")
        if guid.startswith("g"):
            chat_type = ChatType.GROUP
        elif guid.startswith("c"):
            chat_type = ChatType.CHANNEL
        elif guid.startswith("b"):
            chat_type = ChatType.BOT
        else:
            chat_type = ChatType.PRIVATE

        return cls(
            client=client,
            id=guid,
            type=chat_type,
            title=data.get("title"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            username=data.get("username"),
            members_count=data.get("count_members"),
            description=data.get("description"),
        )
