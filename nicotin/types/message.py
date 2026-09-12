from __future__ import annotations

from .object import Object
from .user import User
from .file import File
from ..enums import MessageType


class Message(Object):
    """
    An incoming or outgoing message, shaped like Pyrogram's ``Message``.

    Only the fields relevant to ``message_type`` are populated — e.g.
    ``photo`` is only set when ``message_type is MessageType.PHOTO``.

    :param id: the message id (``message_id``) inside its chat.
    :param chat_id: the ``object_guid`` of the chat the message belongs to.
    :param from_user: the :class:`~nicotin.types.User` who sent it.
    :param date: unix timestamp the message was sent at.
    :param text: the text content, if any.
    :param message_type: a :class:`~nicotin.enums.MessageType`.
    :param photo: attached photo, as a :class:`~nicotin.types.File`.
    :param video: attached video, as a :class:`~nicotin.types.File`.
    :param document: attached generic file, as a :class:`~nicotin.types.File`.
    :param reply_to_message_id: id of the message this one replies to, if any.
    :param is_edited: whether the message has been edited.
    :param forwarded_from: :class:`~nicotin.types.User` this message was forwarded from, if any.
    """

    def __init__(
        self,
        *,
        client=None,
        id: str,
        chat_id: str,
        from_user: User | None = None,
        date: int | None = None,
        text: str | None = None,
        message_type: MessageType = MessageType.TEXT,
        photo: File | None = None,
        video: File | None = None,
        document: File | None = None,
        voice: File | None = None,
        reply_to_message_id: str | None = None,
        is_edited: bool = False,
        forwarded_from: User | None = None,
    ):
        self._client = client
        self.id = id
        self.chat_id = chat_id
        self.from_user = from_user
        self.date = date
        self.text = text
        self.message_type = message_type
        self.photo = photo
        self.video = video
        self.document = document
        self.voice = voice
        self.reply_to_message_id = reply_to_message_id
        self.is_edited = is_edited
        self.forwarded_from = forwarded_from

    # ------------------------------------------------------------------
    # Pyrogram-style bound shortcuts — everything just delegates to the
    # Client that produced this Message, filling in chat_id/message_id.
    # ------------------------------------------------------------------

    async def reply(self, text: str, **kwargs):
        """Reply in the same chat, quoting this message."""
        return await self._client.send_message(
            self.chat_id, text, reply_to_message_id=self.id, **kwargs
        )

    reply_text = reply  # alias, exactly like Pyrogram's Message.reply_text

    async def reply_photo(self, photo: str, **kwargs):
        return await self._client.send_photo(
            self.chat_id, photo, reply_to_message_id=self.id, **kwargs
        )

    async def reply_video(self, video: str, **kwargs):
        return await self._client.send_video(
            self.chat_id, video, reply_to_message_id=self.id, **kwargs
        )

    async def reply_document(self, document: str, **kwargs):
        return await self._client.send_document(
            self.chat_id, document, reply_to_message_id=self.id, **kwargs
        )

    async def edit_text(self, text: str, **kwargs):
        return await self._client.edit_message_text(self.chat_id, self.id, text, **kwargs)

    edit = edit_text

    async def delete(self, revoke: bool = True):
        return await self._client.delete_messages(self.chat_id, [self.id], revoke=revoke)

    async def forward(self, chat_id: str):
        return await self._client.forward_messages(chat_id, self.chat_id, [self.id])

    async def pin(self):
        return await self._client.pin_chat_message(self.chat_id, self.id)

    async def download(self, file_path: str | None = None) -> str:
        """Download this message's media (photo/video/document/voice)."""
        media = self.photo or self.video or self.document or self.voice
        if media is None:
            raise ValueError("Message has no downloadable media")
        return await media.download(file_path)

    @property
    def media(self) -> File | None:
        """Whichever :class:`~nicotin.types.File` this message carries, or ``None``."""
        return self.photo or self.video or self.document or self.voice

    @classmethod
    def _parse(cls, client, data: dict, chat_id: str) -> "Message":
        msg_type = MessageType.TEXT
        photo = video = document = voice = None

        file_data = data.get("file_inline")
        if file_data:
            mime = (file_data.get("mime") or "").lower()
            f = File._parse(client, file_data)
            if mime in ("jpg", "jpeg", "png"):
                msg_type, photo = MessageType.PHOTO, f
            elif mime in ("mp4",):
                msg_type, video = MessageType.VIDEO, f
            elif file_data.get("type") == "Voice":
                msg_type, voice = MessageType.VOICE, f
            else:
                msg_type, document = MessageType.FILE, f

        sender = None
        if "author_object_guid" in data:
            sender = User(client=client, id=data["author_object_guid"], first_name="")

        return cls(
            client=client,
            id=data.get("message_id", ""),
            chat_id=chat_id,
            from_user=sender,
            date=data.get("time"),
            text=data.get("text"),
            message_type=msg_type,
            photo=photo,
            video=video,
            document=document,
            voice=voice,
            reply_to_message_id=data.get("reply_to_message_id"),
            is_edited=data.get("is_edited", False),
        )
