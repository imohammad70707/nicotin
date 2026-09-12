"""
NICOTIN
~~~~~~~

An async Python library for the Rubika messenger, with an API surface
(method names, property names, filters, handler system, docs style)
deliberately modeled after the Telegram bot ecosystem (Pyrogram /
python-telegram-bot), so anyone coming from Telegram bot development
feels at home immediately.

    from nicotin import Client, filters

    app = Client("my_account", auth="XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX")

    @app.on_message(filters.text & filters.private)
    async def echo(client, message):
        await message.reply(message.text)

    app.run()

:copyright: NICOTIN contributors
:license: MIT
"""

from .client import Client
from .types import Update, Message, User, Chat, File, CallbackQuery
from . import filters
from . import enums
from .errors import NicotinError, RPCError, AuthError, FloodWait

__all__ = [
    "Client",
    "Update",
    "Message",
    "User",
    "Chat",
    "File",
    "CallbackQuery",
    "filters",
    "enums",
    "NicotinError",
    "RPCError",
    "AuthError",
    "FloodWait",
]

__version__ = "0.1.0"
