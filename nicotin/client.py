"""
nicotin.client
~~~~~~~~~~~~~~~

The :class:`Client` class: NICOTIN's single entry point, deliberately
shaped like ``pyrogram.Client`` — same method names, same decorator
style, same ``run()`` convenience, same "everything is a coroutine"
philosophy — but talking to Rubika instead of Telegram.
"""

from __future__ import annotations

import asyncio
import inspect
from pathlib import Path
from typing import Callable

from .network import Session
from .types import Message, Chat, User, File, CallbackQuery, Update
from .enums import ChatType, ChatActivity, ParseMode
from .filters import Filter, all as filters_all
from .handlers import (
    Handler,
    MessageHandler,
    EditedMessageHandler,
    DeletedMessagesHandler,
    CallbackQueryHandler,
)
from .errors import AuthError


class Client:
    """
    NICOTIN's main class — one instance per Rubika account/bot.

    :param name: a local session name, used for the ``{name}.session`` file.
    :param auth: the account's auth key. If omitted, NICOTIN will look
        for a saved ``{name}.session`` file on disk.
    :param platform: reported client platform (``"web"``, ``"android"``, ``"rubx"``).
    :param workers: number of concurrent update-dispatch workers, exactly
        like Pyrogram's own ``workers`` parameter.

    Example::

        from nicotin import Client, filters

        app = Client("my_account", auth="...")

        @app.on_message(filters.command("start"))
        async def start(client, message):
            await message.reply("سلام از نیکوتین 👋")

        app.run()
    """

    def __init__(
        self,
        name: str,
        auth: str | None = None,
        *,
        platform: str = "web",
        workers: int = 4,
        session_dir: str = ".",
    ):
        self.name = name
        self.workers = workers
        self.session_dir = Path(session_dir)
        self._auth = auth or self._load_session()
        if not self._auth:
            raise AuthError(
                f"No auth key provided and no session file found for '{name}'. "
                f"Pass auth=... on first run."
            )

        self.session = Session(self._auth, platform=platform)
        self._handlers: list[Handler] = []
        self._polling_task: asyncio.Task | None = None
        self.me: User | None = None

    # ------------------------------------------------------------------
    # Session persistence
    # ------------------------------------------------------------------

    def _session_path(self) -> Path:
        return self.session_dir / f"{self.name}.session"

    def _load_session(self) -> str | None:
        path = self._session_path()
        return path.read_text().strip() if path.exists() else None

    def _save_session(self):
        self._session_path().write_text(self._auth)

    # ------------------------------------------------------------------
    # Lifecycle — mirrors pyrogram.Client.start / stop / run / idle
    # ------------------------------------------------------------------

    async def start(self) -> "Client":
        """Connect and begin listening for updates. Returns ``self`` for chaining."""
        self._save_session()
        self.me = await self.get_me()
        self._polling_task = asyncio.create_task(self._update_loop())
        return self

    async def stop(self):
        """Disconnect and stop dispatching updates."""
        if self._polling_task:
            self._polling_task.cancel()
        await self.session.close()

    def run(self, coroutine=None):
        """
        Blocking helper exactly like ``pyrogram.Client.run()``: starts the
        client, optionally awaits ``coroutine``, then idles until Ctrl+C.
        """
        async def _runner():
            await self.start()
            try:
                if coroutine:
                    await coroutine
                else:
                    await self._idle()
            finally:
                await self.stop()

        asyncio.run(_runner())

    async def _idle(self):
        try:
            while True:
                await asyncio.sleep(3600)
        except asyncio.CancelledError:
            pass

    async def _update_loop(self):
        """Long-polls for new updates and dispatches them to handlers."""
        while True:
            try:
                raw_updates = await self.session.invoke("getUpdates", {"limit": 100})
                for raw in raw_updates.get("updates", []):
                    update = self._parse_update(raw)
                    await self._dispatch(update)
            except asyncio.CancelledError:
                raise
            except Exception:
                # A production client would log this; kept silent here
                # to match a minimal skeleton.
                pass
            await asyncio.sleep(1)

    def _parse_update(self, raw: dict) -> Update:
        update_type = raw.get("type")
        chat_id = raw.get("object_guid", "")

        if update_type == "NewMessage":
            return Update(message=Message._parse(self, raw.get("message", {}), chat_id))
        if update_type == "EditedMessage":
            return Update(edited_message=Message._parse(self, raw.get("message", {}), chat_id))
        if update_type == "RemovedMessage":
            return Update(deleted_message_ids=raw.get("message_ids", []))
        if update_type == "CallbackQuery":
            msg = Message._parse(self, raw.get("message", {}), chat_id)
            cq = CallbackQuery(
                client=self,
                id=raw.get("callback_id", ""),
                from_user=User(client=self, id=raw.get("user_guid", ""), first_name=""),
                message=msg,
                data=raw.get("data", ""),
            )
            return Update(callback_query=cq)
        return Update()

    async def _dispatch(self, update: Update):
        target = (
            update.message
            or update.edited_message
            or update.callback_query
            or update.deleted_message_ids
        )
        for handler in self._handlers:
            if update.message and isinstance(handler, MessageHandler):
                event = update.message
            elif update.edited_message and isinstance(handler, EditedMessageHandler):
                event = update.edited_message
            elif update.callback_query and isinstance(handler, CallbackQueryHandler):
                event = update.callback_query
            elif update.deleted_message_ids and isinstance(handler, DeletedMessagesHandler):
                event = update.deleted_message_ids
            else:
                continue

            if isinstance(event, Message) or isinstance(event, CallbackQuery):
                matched = await handler.check(self, getattr(event, "message", event) if isinstance(event, CallbackQuery) else event)
            else:
                matched = True

            if matched:
                await handler.callback(self, event)

    # ------------------------------------------------------------------
    # Handler registration — decorators mirror pyrogram.Client exactly
    # ------------------------------------------------------------------

    def add_handler(self, handler: Handler):
        self._handlers.append(handler)
        return handler

    def remove_handler(self, handler: Handler):
        self._handlers.remove(handler)

    def on_message(self, filters: Filter = filters_all):
        def decorator(func: Callable):
            self.add_handler(MessageHandler(func, filters))
            return func
        return decorator

    def on_edited_message(self, filters: Filter = filters_all):
        def decorator(func: Callable):
            self.add_handler(EditedMessageHandler(func, filters))
            return func
        return decorator

    def on_deleted_messages(self):
        def decorator(func: Callable):
            self.add_handler(DeletedMessagesHandler(func))
            return func
        return decorator

    def on_callback_query(self, filters: Filter = filters_all):
        def decorator(func: Callable):
            self.add_handler(CallbackQueryHandler(func, filters))
            return func
        return decorator

    # ------------------------------------------------------------------
    # API methods — names/signatures mirror pyrogram.Client's own
    # ------------------------------------------------------------------

    async def get_me(self) -> User:
        """Fetch info about the currently logged-in account."""
        data = await self.session.invoke("getUserInfo", {})
        return User._parse(self, data.get("user", {}))

    async def send_message(
        self,
        chat_id: str,
        text: str,
        *,
        reply_to_message_id: str | None = None,
        parse_mode: ParseMode = ParseMode.NONE,
    ) -> Message:
        """Send a text message to ``chat_id``."""
        data = {"object_guid": chat_id, "text": text, "rnd": _rnd()}
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
        result = await self.session.invoke("sendMessage", data)
        return Message._parse(self, result, chat_id)

    async def send_photo(self, chat_id: str, photo: str, *, caption: str | None = None, **kwargs) -> Message:
        """Send a photo (local path or previously uploaded ``file_id``) to ``chat_id``."""
        return await self._send_media(chat_id, photo, "Image", caption=caption, **kwargs)

    async def send_video(self, chat_id: str, video: str, *, caption: str | None = None, **kwargs) -> Message:
        return await self._send_media(chat_id, video, "Video", caption=caption, **kwargs)

    async def send_voice(self, chat_id: str, voice: str, **kwargs) -> Message:
        return await self._send_media(chat_id, voice, "Voice", **kwargs)

    async def send_document(self, chat_id: str, document: str, *, caption: str | None = None, **kwargs) -> Message:
        return await self._send_media(chat_id, document, "File", caption=caption, **kwargs)

    async def _send_media(
        self,
        chat_id: str,
        media: str,
        media_type: str,
        *,
        caption: str | None = None,
        reply_to_message_id: str | None = None,
    ) -> Message:
        file_id = await self._upload(media)
        data = {
            "object_guid": chat_id,
            "rnd": _rnd(),
            "file_inline": {"file_id": file_id, "type": media_type},
        }
        if caption:
            data["text"] = caption
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
        result = await self.session.invoke("sendMessage", data)
        return Message._parse(self, result, chat_id)

    async def _upload(self, path: str) -> str:
        """Upload a local file to Rubika's storage and return its ``file_id``."""
        result = await self.session.invoke("requestSendFile", {"file_name": Path(path).name})
        return result.get("file_id", "")

    async def download_media(self, file: File, file_path: str | None = None) -> str:
        """Download ``file`` to ``file_path`` (or the file's own name) and return the local path."""
        dest = file_path or (file.name or file.id)
        result = await self.session.invoke(
            "requestFile", {"file_id": file.id, "access_hash_rec": file.access_hash_rec}
        )
        Path(dest).write_bytes(result.get("bytes", b""))
        return dest

    async def edit_message_text(self, chat_id: str, message_id: str, text: str) -> Message:
        result = await self.session.invoke(
            "editMessage", {"object_guid": chat_id, "message_id": message_id, "text": text}
        )
        return Message._parse(self, result, chat_id)

    async def delete_messages(self, chat_id: str, message_ids: list[str], *, revoke: bool = True):
        return await self.session.invoke(
            "deleteMessages",
            {"object_guid": chat_id, "message_ids": message_ids, "type": "Global" if revoke else "Local"},
        )

    async def forward_messages(self, to_chat_id: str, from_chat_id: str, message_ids: list[str]):
        return await self.session.invoke(
            "forwardMessages",
            {
                "from_object_guid": from_chat_id,
                "to_object_guid": to_chat_id,
                "message_ids": message_ids,
                "rnd": _rnd(),
            },
        )

    async def get_chat(self, chat_id: str) -> Chat:
        """Fetch full info about a chat, group or channel."""
        data = await self.session.invoke("getObjectInfo", {"object_guid": chat_id})
        return Chat._parse(self, data)

    async def get_chat_history(self, chat_id: str, *, limit: int = 50) -> list[Message]:
        data = await self.session.invoke(
            "getMessages", {"object_guid": chat_id, "limit": limit}
        )
        return [Message._parse(self, m, chat_id) for m in data.get("messages", [])]

    async def ban_chat_member(self, chat_id: str, user_id: str):
        return await self.session.invoke(
            "banGroupMember", {"group_guid": chat_id, "member_guid": user_id, "action": "Set"}
        )

    async def unban_chat_member(self, chat_id: str, user_id: str):
        return await self.session.invoke(
            "banGroupMember", {"group_guid": chat_id, "member_guid": user_id, "action": "Unset"}
        )

    async def leave_chat(self, chat_id: str):
        return await self.session.invoke("leaveGroup", {"group_guid": chat_id})

    async def pin_chat_message(self, chat_id: str, message_id: str):
        return await self.session.invoke(
            "setPinMessage", {"object_guid": chat_id, "message_id": message_id, "action": "Pin"}
        )

    async def send_chat_action(self, chat_id: str, action: ChatActivity = ChatActivity.TYPING):
        """Show a typing/recording/uploading indicator, like Pyrogram's ``send_chat_action``."""
        return await self.session.invoke(
            "sendChatActivity", {"object_guid": chat_id, "activity": action.value}
        )

    async def answer_callback_query(self, callback_query_id: str, *, text: str | None = None, show_alert: bool = False):
        return await self.session.invoke(
            "answerCallback",
            {"callback_id": callback_query_id, "text": text, "show_alert": show_alert},
        )


def _rnd() -> int:
    import random
    return random.randint(100000, 999999999)
