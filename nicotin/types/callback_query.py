from __future__ import annotations

from .object import Object
from .user import User
from .message import Message


class CallbackQuery(Object):
    """
    An incoming callback from an inline keyboard button press, shaped
    like Pyrogram's ``CallbackQuery``.

    :param id: unique id of this callback event.
    :param from_user: the :class:`~nicotin.types.User` who tapped the button.
    :param message: the :class:`~nicotin.types.Message` the keyboard was attached to.
    :param data: the developer-defined payload of the button that was pressed.
    """

    def __init__(self, *, client=None, id: str, from_user: User, message: Message, data: str):
        self._client = client
        self.id = id
        self.from_user = from_user
        self.message = message
        self.data = data

    async def answer(self, text: str | None = None, show_alert: bool = False):
        return await self._client.answer_callback_query(
            self.id, text=text, show_alert=show_alert
        )

    async def edit_message_text(self, text: str, **kwargs):
        return await self._client.edit_message_text(
            self.message.chat_id, self.message.id, text, **kwargs
        )
