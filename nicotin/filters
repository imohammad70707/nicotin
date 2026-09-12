"""
nicotin.filters
~~~~~~~~~~~~~~~

Composable message filters, an exact conceptual copy of Pyrogram's
``filters`` module: each filter is a small callable object that can be
combined with ``&``, ``|`` and ``~``.

    from nicotin import filters

    @app.on_message(filters.text & filters.private & ~filters.bot)
    async def handler(client, message): ...
"""

from __future__ import annotations

import re
from typing import Callable, Pattern

from .enums import ChatType, MessageType
from .types import Message


class Filter:
    """Base class for every filter. Wraps a plain callable and supports ``& | ~``."""

    def __init__(self, func: Callable[["Filter", "Client", Message], bool], name: str | None = None):
        self.func = func
        self.name = name or getattr(func, "__name__", "Filter")

    async def __call__(self, client, message: Message) -> bool:
        result = self.func(self, client, message)
        if hasattr(result, "__await__"):
            result = await result
        return bool(result)

    def __and__(self, other: "Filter") -> "Filter":
        return Filter(lambda _, c, m: _and(self, other, c, m), name=f"({self.name} & {other.name})")

    def __or__(self, other: "Filter") -> "Filter":
        return Filter(lambda _, c, m: _or(self, other, c, m), name=f"({self.name} | {other.name})")

    def __invert__(self) -> "Filter":
        return Filter(lambda _, c, m: _not(self, c, m), name=f"(~{self.name})")

    def __repr__(self) -> str:
        return f"nicotin.filters.{self.name}"


async def _and(f1: Filter, f2: Filter, client, message) -> bool:
    return await f1(client, message) and await f2(client, message)


async def _or(f1: Filter, f2: Filter, client, message) -> bool:
    return await f1(client, message) or await f2(client, message)


async def _not(f: Filter, client, message) -> bool:
    return not await f(client, message)


def create(func: Callable, name: str | None = None) -> Filter:
    """Build a custom filter out of a plain ``def f(filt, client, message) -> bool``."""
    return Filter(func, name)


# ---------------------------------------------------------------------
# Ready-made filters — names deliberately match Pyrogram's own filters
# ---------------------------------------------------------------------

all = create(lambda _, c, m: True, "all")
me = create(lambda _, c, m: False, "me")  # overridden per-client at dispatch time

text = create(lambda _, c, m: m.message_type == MessageType.TEXT and bool(m.text), "text")
photo = create(lambda _, c, m: m.message_type == MessageType.PHOTO, "photo")
video = create(lambda _, c, m: m.message_type == MessageType.VIDEO, "video")
voice = create(lambda _, c, m: m.message_type == MessageType.VOICE, "voice")
document = create(lambda _, c, m: m.message_type == MessageType.FILE, "document")
media = create(lambda _, c, m: m.media is not None, "media")

private = create(lambda _, c, m: str(m.chat_id).startswith("u"), "private")
group = create(lambda _, c, m: str(m.chat_id).startswith("g"), "group")
channel = create(lambda _, c, m: str(m.chat_id).startswith("c"), "channel")
bot = create(lambda _, c, m: str(m.chat_id).startswith("b"), "bot")

edited = create(lambda _, c, m: m.is_edited, "edited")
reply = create(lambda _, c, m: m.reply_to_message_id is not None, "reply")
forwarded = create(lambda _, c, m: m.forwarded_from is not None, "forwarded")


def command(commands: str | list[str], prefixes: str | list[str] = "/") -> Filter:
    """
    Match messages starting with a bot command, e.g. ``filters.command("start")``.

    :param commands: one command or a list of them, without the prefix.
    :param prefixes: one prefix or a list of them (default ``"/"``).
    """
    cmds = {c.lower() for c in ([commands] if isinstance(commands, str) else commands)}
    pfx = [prefixes] if isinstance(prefixes, str) else prefixes

    def func(_, c, m: Message) -> bool:
        if not m.text:
            return False
        for p in pfx:
            if m.text.startswith(p):
                first_word = m.text[len(p):].split(maxsplit=1)[0].lower()
                if first_word in cmds:
                    return True
        return False

    return create(func, f"command({commands!r})")


def regex(pattern: str | Pattern, flags: int = 0) -> Filter:
    """Match messages whose text matches a regular expression."""
    compiled = pattern if isinstance(pattern, re.Pattern) else re.compile(pattern, flags)

    def func(_, c, m: Message) -> bool:
        return bool(m.text and compiled.search(m.text))

    return create(func, f"regex({pattern!r})")


def user(users: str | list[str]) -> Filter:
    """Match messages sent by one of the given user ``object_guid``\\ s."""
    ids = {users} if isinstance(users, str) else set(users)

    def func(_, c, m: Message) -> bool:
        return bool(m.from_user and m.from_user.id in ids)

    return create(func, f"user({users!r})")


def chat(chats: str | list[str]) -> Filter:
    """Match messages coming from one of the given chat ``object_guid``\\ s."""
    ids = {chats} if isinstance(chats, str) else set(chats)

    def func(_, c, m: Message) -> bool:
        return m.chat_id in ids

    return create(func, f"chat({chats!r})")
