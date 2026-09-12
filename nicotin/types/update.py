from __future__ import annotations

from .object import Object
from .message import Message
from .callback_query import CallbackQuery


class Update(Object):
    """
    A single raw event coming from Rubika's long-poll/websocket layer,
    already normalized into one of ``message`` / ``edited_message`` /
    ``callback_query``, mirroring Pyrogram's internal ``Update`` handling
    (there, it's hidden — here it's exposed for advanced use via
    ``@app.on_update()``).

    Only one of the fields below is set per instance.
    """

    def __init__(
        self,
        *,
        message: Message | None = None,
        edited_message: Message | None = None,
        deleted_message_ids: list[str] | None = None,
        callback_query: CallbackQuery | None = None,
    ):
        self.message = message
        self.edited_message = edited_message
        self.deleted_message_ids = deleted_message_ids
        self.callback_query = callback_query
