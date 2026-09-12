"""
nicotin.client
~~~~~~~~~~~~~~~

The :class:`Client` class: NICOTIN's single entry point, deliberately
shaped like ``pyrogram.Client`` — same method names, same decorator
style, same ``run()`` convenience, same "everything is a coroutine"
philosophy — but talking to Rubika's official **Bot API** with a
**bot token** (the credential you get from ``@rubika_bot``), not a
user session/auth key.
"""

from __future__ import annotations

import asyncio
import logging
import time
from pathlib import Path
from typing import Callable

from .network import Session
from .types import Message, Chat, User, File, CallbackQuery, Update
from .enums import ParseMode  # noqa: F401 (kept in signatures for future use)
from .filters import Filter, all as filters_all
from .handlers import (
    Handler,
    MessageHandler,
    EditedMessageHandler,
    DeletedMessagesHandler,
    CallbackQueryHandler,
)
from .errors import AuthError, RPCError, FloodWait, ConnectionError_, RequestTimeout

logger = logging.getLogger("nicotin")
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("[NICOTIN] %(asctime)s %(levelname)s: %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)


class Client:
    """
    NICOTIN's main class — one instance per Rubika **bot**.

    :param bot_token: the token Rubika Bot (``@rubika_bot``) gave you when
        you created your bot. This is the only credential needed — there
        is no login/OTP step and nothing gets saved to disk.
    :param base_url: override the Bot API base URL, if you're pointed at
        a different endpoint than the default.
    :param workers: number of concurrent update-dispatch workers, exactly
        like Pyrogram's own ``workers`` parameter.

    Example::

        from nicotin import Client, filters

        app = Client(bot_token="123456:AbCdEf...")

        @app.on_message(filters.command("start"))
        async def start(client, message):
            await message.reply("سلام از نیکوتین 👋")

        app.run()
    """

    def __init__(
        self,
        bot_token: str,
        *,
        base_url: str | None = None,
        workers: int = 4,
    ):
        if not bot_token:
            raise AuthError(
                "No bot_token provided. Create a bot with @rubika_bot on "
                "Rubika and pass the token it gives you as bot_token=...."
            )

        self.bot_token = bot_token
        self.workers = workers
        self.session = Session(bot_token, base_url=base_url) if base_url else Session(bot_token)
        self._handlers: list[Handler] = []
        self._polling_task: asyncio.Task | None = None
        self._next_offset_id: str | None = None
        self.me: User | None = None

    # ------------------------------------------------------------------
    # Lifecycle — mirrors pyrogram.Client.start / stop / run / idle
    # ------------------------------------------------------------------

    async def start(self) -> "Client":
        """
        Verify the bot token and begin listening for updates. Returns ``self``.

        Logs a clear success/failure message so it's obvious whether the
        bot actually came online, instead of failing silently.
        """
        logger.info("در حال اتصال به Rubika Bot API ...")
        started_at = time.monotonic()
        try:
            self.me = await self.get_me()
        except AuthError as e:
            logger.error(f"توکن بات نامعتبر است، اجرا متوقف شد: {e}")
            raise
        except RequestTimeout as e:
            logger.error(f"اتصال به سرور روبیکا تایم‌اوت شد، ربات اجرا نشد: {e}")
            raise
        except ConnectionError_ as e:
            logger.error(f"اتصال به سرور روبیکا برقرار نشد، ربات اجرا نشد: {e}")
            raise
        except RPCError as e:
            logger.error(f"سرور روبیکا خطا برگرداند، ربات اجرا نشد: {e}")
            raise

        elapsed = time.monotonic() - started_at
        who = f"@{self.me.username}" if self.me and self.me.username else (self.me.first_name if self.me else "")
        logger.info(f"ربات {who} با موفقیت متصل شد ✅ ({elapsed:.2f}s) — شروع دریافت پیام‌ها ...")

        self._polling_task = asyncio.create_task(self._update_loop())
        return self

    async def stop(self):
        """Stop dispatching updates and close the underlying HTTP session."""
        logger.info("در حال متوقف کردن ربات ...")
        if self._polling_task:
            self._polling_task.cancel()
        await self.session.close()
        logger.info("ربات متوقف شد.")

    def run(self, coroutine=None):
        """
        Blocking helper exactly like ``pyrogram.Client.run()``: starts the
        bot, optionally awaits ``coroutine``, then idles until Ctrl+C.
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
        """Long-polls ``getUpdates`` and dispatches new updates to handlers."""
        consecutive_errors = 0
        while True:
            try:
                params = {"limit": 100}
                if self._next_offset_id:
                    params["offset_id"] = self._next_offset_id

                result = await self.session.invoke("getUpdates", params)
                raw_updates = result.get("updates", [])
                for raw in raw_updates:
                    update = self._parse_update(raw)
                    await self._dispatch(update)
                if raw_updates:
                    self._next_offset_id = raw_updates[-1].get("next_offset_id") or result.get("next_offset_id")
                consecutive_errors = 0
            except asyncio.CancelledError:
                raise
            except RequestTimeout as e:
                consecutive_errors += 1
                logger.warning(f"تایم‌اوت هنگام دریافت آپدیت‌ها (تلاش ناموفق #{consecutive_errors}): {e}")
            except FloodWait as e:
                logger.warning(f"محدودیت نرخ درخواست از سمت روبیکا — {e.value} ثانیه صبر می‌کنیم ...")
                await asyncio.sleep(e.value)
                continue
            except ConnectionError_ as e:
                consecutive_errors += 1
                logger.error(f"قطعی شبکه هنگام دریافت آپدیت‌ها (تلاش ناموفق #{consecutive_errors}): {e}")
            except RPCError as e:
                consecutive_errors += 1
                logger.error(f"خطای API روبیکا هنگام دریافت آپدیت‌ها: {e}")
            except Exception as e:
                consecutive_errors += 1
                logger.exception(f"خطای غیرمنتظره در حلقه‌ی دریافت آپدیت: {e}")
            await asyncio.sleep(1)

    def _parse_update(self, raw: dict) -> Update:
        update_type = raw.get("type")
        chat_id = raw.get("chat_id", "")

        if update_type in ("NewMessage", "StartedBot"):
            return Update(message=Message._parse(self, raw.get("new_message", raw.get("message", {})), chat_id))
        if update_type in ("UpdatedMessage", "EditedMessage"):
            return Update(edited_message=Message._parse(self, raw.get("updated_message", raw.get("message", {})), chat_id))
        if update_type == "RemovedMessage":
            return Update(deleted_message_ids=[raw.get("removed_message_id")] if raw.get("removed_message_id") else [])
        if update_type in ("ButtonClicked", "CallbackQuery"):
            msg = Message._parse(self, raw.get("message", {}), chat_id)
            cq = CallbackQuery(
                client=self,
                id=raw.get("callback_id", raw.get("button_id", "")),
                from_user=User(client=self, id=raw.get("chat_id", ""), first_name=""),
                message=msg,
                data=raw.get("data", raw.get("button_id", "")),
            )
            return Update(callback_query=cq)
        return Update()

    async def _dispatch(self, update: Update):
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

            if isinstance(event, (Message, CallbackQuery)):
                check_target = event.message if isinstance(event, CallbackQuery) else event
                matched = await handler.check(self, check_target)
            else:
                matched = True

            if matched:
                try:
                    await handler.callback(self, event)
                except Exception as e:
                    logger.exception(f"خطا داخل هندلر '{handler.callback.__name__}': {e}")

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
    # API methods — names/signatures mirror pyrogram.Client's own,
    # bodies match Rubika's official Bot API vocabulary (chat_id, not
    # object_guid; no group-admin methods, since a bot token doesn't
    # carry a user's admin permissions).
    # ------------------------------------------------------------------

    async def get_me(self) -> User:
        """Fetch info about this bot itself."""
        data = await self.session.invoke("getMe", {})
        return User._parse(self, data.get("bot", data))

    async def send_message(
        self,
        chat_id: str,
        text: str,
        *,
        reply_to_message_id: str | None = None,
        parse_mode: ParseMode = ParseMode.NONE,
    ) -> Message:
        """Send a text message to ``chat_id``."""
        data = {"chat_id": chat_id, "text": text}
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
        result = await self.session.invoke("sendMessage", data)
        return Message._parse(self, result, chat_id)

    async def send_photo(self, chat_id: str, photo: str, *, caption: str | None = None, **kwargs) -> Message:
        """Send a photo (local path) to ``chat_id``."""
        return await self._send_media(chat_id, photo, "sendFile", caption=caption, **kwargs)

    async def send_video(self, chat_id: str, video: str, *, caption: str | None = None, **kwargs) -> Message:
        return await self._send_media(chat_id, video, "sendFile", caption=caption, **kwargs)

    async def send_voice(self, chat_id: str, voice: str, **kwargs) -> Message:
        return await self._send_media(chat_id, voice, "sendFile", **kwargs)

    async def send_document(self, chat_id: str, document: str, *, caption: str | None = None, **kwargs) -> Message:
        return await self._send_media(chat_id, document, "sendFile", caption=caption, **kwargs)

    async def _send_media(
        self,
        chat_id: str,
        media: str,
        method: str,
        *,
        caption: str | None = None,
        reply_to_message_id: str | None = None,
    ) -> Message:
        file_id = await self._upload(chat_id, media)
        data = {"chat_id": chat_id, "file_id": file_id}
        if caption:
            data["text"] = caption
        if reply_to_message_id:
            data["reply_to_message_id"] = reply_to_message_id
        result = await self.session.invoke(method, data)
        return Message._parse(self, result, chat_id)

    async def _upload(self, chat_id: str, path: str) -> str:
        """
        Upload a local file for ``chat_id`` and return its ``file_id``,
        following the Bot API's two-step ``requestSendFile`` + upload flow.
        """
        request = await self.session.invoke(
            "requestSendFile", {"type": "File", "file_name": Path(path).name}
        )
        upload_url = request.get("upload_url", "")
        uploaded = await self.session.upload_file(upload_url, path)
        return uploaded.get("file_id", request.get("file_id", ""))

    async def download_media(self, file: File, file_path: str | None = None) -> str:
        """Download ``file`` to ``file_path`` (or the file's own name) and return the local path."""
        dest = file_path or (file.name or file.id)
        result = await self.session.invoke("getFile", {"file_id": file.id})
        Path(dest).write_bytes(result.get("bytes", b""))
        return dest

    async def edit_message_text(self, chat_id: str, message_id: str, text: str) -> Message:
        result = await self.session.invoke(
            "editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": text}
        )
        return Message._parse(self, result, chat_id)

    async def delete_messages(self, chat_id: str, message_ids: list[str], **_ignored):
        """Delete one or more messages. (Bots can only delete their own messages.)"""
        return await self.session.invoke(
            "deleteMessage", {"chat_id": chat_id, "message_id": message_ids[0]}
        ) if len(message_ids) == 1 else await asyncio.gather(
            *(self.session.invoke("deleteMessage", {"chat_id": chat_id, "message_id": mid}) for mid in message_ids)
        )

    async def forward_messages(self, to_chat_id: str, from_chat_id: str, message_ids: list[str]):
        return await asyncio.gather(*(
            self.session.invoke(
                "forwardMessage",
                {"from_chat_id": from_chat_id, "to_chat_id": to_chat_id, "message_id": mid},
            )
            for mid in message_ids
        ))

    async def get_chat(self, chat_id: str) -> Chat:
        """Fetch info about a chat the bot is a member of."""
        data = await self.session.invoke("getChat", {"chat_id": chat_id})
        return Chat._parse(self, data.get("chat", data))

    async def get_chat_history(self, chat_id: str, *, limit: int = 50) -> list[Message]:
        data = await self.session.invoke("getChatHistory", {"chat_id": chat_id, "limit": limit})
        return [Message._parse(self, m, chat_id) for m in data.get("messages", [])]

    async def answer_callback_query(self, callback_query_id: str, *, text: str | None = None, show_alert: bool = False):
        return await self.session.invoke(
            "answerCallback",
            {"callback_id": callback_query_id, "text": text, "show_alert": show_alert},
        )

    async def set_webhook(self, url: str, update_types: list[str] | None = None):
        """Register a webhook URL for updates, instead of long-polling ``getUpdates``."""
        return await self.session.invoke(
            "updateBotEndpoints", {"url": url, "type": update_types or ["ReceiveUpdate"]}
        )
