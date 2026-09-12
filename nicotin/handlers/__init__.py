"""
nicotin.handlers
~~~~~~~~~~~~~~~~

Handler classes, one per update kind, mirroring Pyrogram's
``handlers`` package. You rarely build these directly — use the
``@app.on_message()`` / ``@app.on_callback_query()`` decorators on
:class:`~nicotin.Client` instead, which build these for you.
"""

from typing import Callable

from ..filters import Filter, all as filters_all


class Handler:
    """Base class for every handler kind."""

    def __init__(self, callback: Callable, filters: Filter | None = None):
        self.callback = callback
        self.filters = filters or filters_all

    async def check(self, client, update) -> bool:
        return await self.filters(client, update)


class MessageHandler(Handler):
    """Fires ``callback(client, message)`` for new incoming messages."""


class EditedMessageHandler(Handler):
    """Fires ``callback(client, message)`` when a message gets edited."""


class DeletedMessagesHandler(Handler):
    """Fires ``callback(client, message_ids)`` when messages get deleted."""


class CallbackQueryHandler(Handler):
    """Fires ``callback(client, callback_query)`` for inline button presses."""


__all__ = [
    "Handler",
    "MessageHandler",
    "EditedMessageHandler",
    "DeletedMessagesHandler",
    "CallbackQueryHandler",
]
