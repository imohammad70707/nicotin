"""
nicotin.enums
~~~~~~~~~~~~~

Enumerations mirroring the shape of Pyrogram's ``enums`` module, adapted
to Rubika's own vocabulary (object_guid types, chat kinds, message
kinds, etc).
"""

from enum import Enum, auto


class ChatType(Enum):
    """The kind of chat / object_guid a message belongs to."""

    PRIVATE = auto()   #: A direct one-to-one chat (``u_...`` guid)
    GROUP = auto()      #: A group chat (``g_...`` guid)
    CHANNEL = auto()     #: A channel (``c_...`` guid)
    BOT = auto()         #: A chat with a bot (``b_...`` guid)


class MessageType(Enum):
    """The content type carried by a :class:`~nicotin.types.Message`."""

    TEXT = auto()
    PHOTO = auto()
    VIDEO = auto()
    GIF = auto()
    VOICE = auto()
    MUSIC = auto()
    FILE = auto()
    STICKER = auto()
    LOCATION = auto()
    CONTACT = auto()
    POLL = auto()
    LIVE_LOCATION = auto()
    FORWARDED = auto()
    DELETED = auto()
    UNKNOWN = auto()


class ChatActivity(Enum):
    """Typing / recording indicator, used with :meth:`Client.send_chat_activity`."""

    TYPING = "Typing"
    RECORDING = "Recording"
    UPLOADING = "Uploading"
    NONE = "None"


class ParseMode(Enum):
    """How :meth:`Client.send_message` should parse ``text`` for entities."""

    NONE = auto()
    MARKDOWN = auto()
    HTML = auto()


class MessageMedia(Enum):
    """Restricts :func:`nicotin.filters` media matching to a specific kind."""

    PHOTO = "Image"
    VIDEO = "Video"
    GIF = "Gif"
    VOICE = "Voice"
    MUSIC = "Music"
    FILE = "File"


__all__ = [
    "ChatType",
    "MessageType",
    "ChatActivity",
    "ParseMode",
    "MessageMedia",
]
