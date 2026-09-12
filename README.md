# NICOTIN

[🇬🇧 English](#-english) | [🇮🇷 فارسی](#-فارسی)

---

# 🇬🇧 English

**Nicotin** is an asynchronous Python library for interacting with the **Rubika** messenger.

Its API is designed with a familiar, Pyrogram-style developer experience, making it easier for developers who are already familiar with Telegram/Pyrogram-style libraries to build Rubika applications.

> 🚧 Nicotin is currently under active development. Some features and API behavior may change in future releases.

## Features

* ⚡ Fully asynchronous API
* 🐍 Python 3.10+
* 💬 Send and receive messages
* 📷 Send photos
* 🎥 Send videos
* 🎤 Send voice messages
* 📁 Send documents/files
* ✏️ Edit messages
* 🗑️ Delete messages
* ↪️ Forward messages
* 📌 Pin messages
* 👥 Chat and member management
* 🔘 Callback query support
* 🔎 Powerful composable filters
* 🧩 Handler-based event system
* 💾 Session persistence
* 🌐 Async HTTP communication using HTTPX

## Installation

Install the latest stable version from PyPI:

```bash
pip install nicotin
```

Or upgrade an existing installation:

```bash
pip install --upgrade nicotin
```

## Quick Start

```python
from nicotin import Client, filters

app = Client(
    "my_account",
    auth="YOUR_AUTH_KEY"
)


@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("سلام! به Nicotin خوش آمدید 👋")


@app.on_message(filters.text & filters.private)
async def echo(client, message):
    await message.reply(message.text)


app.run()
```

## Filters

Nicotin provides composable filters that can be combined using:

* `&` — AND
* `|` — OR
* `~` — NOT

Example:

```python
from nicotin import filters


@app.on_message(
    filters.text
    & filters.private
    & ~filters.bot
)
async def handler(client, message):
    await message.reply(message.text)
```

### Command filter

```python
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("Hello!")
```

Multiple commands are also supported:

```python
@app.on_message(filters.command(["start", "help"]))
async def handler(client, message):
    await message.reply("Command received.")
```

### Regex filter

```python
@app.on_message(filters.regex(r"hello|hi"))
async def handler(client, message):
    await message.reply("Hello!")
```

## Sending Messages

```python
await app.send_message(
    chat_id,
    "Hello from Nicotin!"
)
```

You can also reply directly to a message:

```python
await message.reply("Hello!")
```

## Media

Nicotin provides helpers for sending different types of media:

```python
await app.send_photo(chat_id, photo)
await app.send_video(chat_id, video)
await app.send_voice(chat_id, voice)
await app.send_document(chat_id, document)
```

Messages also provide convenient reply methods:

```python
await message.reply_photo(photo)
await message.reply_video(video)
await message.reply_document(document)
```

## Working With Chats

Example:

```python
chat = await app.get_chat(chat_id)

await chat.send_message("Hello!")

await chat.leave()
```

Depending on the API and permissions, chat-related operations include:

```python
await app.ban_chat_member(chat_id, user_id)
await app.unban_chat_member(chat_id, user_id)
await app.leave_chat(chat_id)
await app.pin_chat_message(chat_id, message_id)
```

## Callback Queries

Nicotin supports callback-query handlers:

```python
@app.on_callback_query()
async def callback(client, query):
    await query.answer("Button clicked!")
```

## Session Files

Nicotin can persist authentication information in a session file.

For example:

```python
app = Client(
    "my_account",
    auth="YOUR_AUTH_KEY"
)
```

The session is saved using the client name:

```text
my_account.session
```

### Security

Never commit authentication keys or session files to GitHub.

Add your session files and environment files to `.gitignore`.

## Updating Nicotin

To upgrade to the latest version:

```bash
pip install --upgrade nicotin
```

Or:

```bash
pip install -U nicotin
```

After a new version is released on PyPI, users can use this command to receive the latest version.

## Current Version

```text
0.1.0
```

The latest released version is available on PyPI:

https://pypi.org/project/nicotin/

## Development

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/nicotin.git
cd nicotin
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Install the package in editable mode:

```bash
pip install -e .
```

## Project Structure

```text
nicotin/
├── nicotin/
│   ├── __init__.py
│   ├── client.py
│   ├── enums/
│   ├── errors/
│   ├── filters.py
│   ├── handlers/
│   ├── network/
│   └── types/
├── tests/
├── README.md
├── LICENSE
├── .gitignore
└── pyproject.toml
```

## Contributing

Contributions, bug reports, feature requests and improvements are welcome.

Before submitting a pull request:

1. Keep changes focused.
2. Follow the existing project style.
3. Add tests when appropriate.
4. Update documentation when behavior changes.

## License

Nicotin is released under the MIT License.

See [`LICENSE`](https://chatgpt.com/c/LICENSE) for the full license text.

## Disclaimer

Nicotin is an independent open-source project.

It is not affiliated with, endorsed by, or sponsored by Rubika or its owners.

## Links

* PyPI: https://pypi.org/project/nicotin/
* GitHub: https://github.com/YOUR_USERNAME/nicotin

---

**Nicotin — An async Python library for Rubika.**

---

# 🇮🇷 فارسی

**Nicotin** یک کتابخانه Python غیرهمزمان برای تعامل با پیام‌رسان **روبیکا** است.

API این کتابخانه با تجربه توسعه‌ای آشنا و مشابه Pyrogram طراحی شده است و به توسعه‌دهندگانی که با کتابخانه‌های سبک Telegram/Pyrogram آشنایی دارند کمک می‌کند تا برنامه‌های روبیکایی خود را راحت‌تر بسازند.

> 🚧 Nicotin در حال حاضر تحت توسعه فعال است. برخی قابلیت‌ها و رفتارهای API ممکن است در نسخه‌های آینده تغییر کنند.

## قابلیت‌ها

* ⚡ API کاملاً غیرهمزمان
* 🐍 پشتیبانی از Python 3.10+
* 💬 ارسال و دریافت پیام
* 📷 ارسال عکس
* 🎥 ارسال ویدیو
* 🎤 ارسال پیام صوتی
* 📁 ارسال فایل و Document
* ✏️ ویرایش پیام‌ها
* 🗑️ حذف پیام‌ها
* ↪️ فوروارد پیام‌ها
* 📌 سنجاق کردن پیام‌ها
* 👥 مدیریت چت و اعضا
* 🔘 پشتیبانی از Callback Query
* 🔎 فیلترهای قدرتمند و قابل ترکیب
* 🧩 سیستم رویداد مبتنی بر Handler
* 💾 ذخیره‌سازی Session
* 🌐 ارتباط HTTP غیرهمزمان با استفاده از HTTPX

## نصب

برای نصب آخرین نسخه پایدار از PyPI:

```bash
pip install nicotin
```

یا برای ارتقای نسخه موجود:

```bash
pip install --upgrade nicotin
```

## شروع سریع

```python
from nicotin import Client, filters

app = Client(
    "my_account",
    auth="YOUR_AUTH_KEY"
)


@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("سلام! به Nicotin خوش آمدید 👋")


@app.on_message(filters.text & filters.private)
async def echo(client, message):
    await message.reply(message.text)


app.run()
```

## فیلترها

Nicotin فیلترهای قابل ترکیبی ارائه می‌دهد که می‌توان آن‌ها را با عملگرهای زیر ترکیب کرد:

* `&` — AND
* `|` — OR
* `~` — NOT

مثال:

```python
from nicotin import filters


@app.on_message(
    filters.text
    & filters.private
    & ~filters.bot
)
async def handler(client, message):
    await message.reply(message.text)
```

### فیلتر Command

```python
@app.on_message(filters.command("start"))
async def start(client, message):
    await message.reply("Hello!")
```

پشتیبانی از چند Command نیز وجود دارد:

```python
@app.on_message(filters.command(["start", "help"]))
async def handler(client, message):
    await message.reply("Command received.")
```

### فیلتر Regex

```python
@app.on_message(filters.regex(r"hello|hi"))
async def handler(client, message):
    await message.reply("Hello!")
```

## ارسال پیام

```python
await app.send_message(
    chat_id,
    "Hello from Nicotin!"
)
```

همچنین می‌توان مستقیماً به یک پیام پاسخ داد:

```python
await message.reply("Hello!")
```

## رسانه‌ها

Nicotin برای ارسال انواع مختلف رسانه Helperهایی ارائه می‌دهد:

```python
await app.send_photo(chat_id, photo)
await app.send_video(chat_id, video)
await app.send_voice(chat_id, voice)
await app.send_document(chat_id, document)
```

پیام‌ها همچنین دارای متدهای ساده برای پاسخ دادن با رسانه هستند:

```python
await message.reply_photo(photo)
await message.reply_video(video)
await message.reply_document(document)
```

## کار با چت‌ها

مثال:

```python
chat = await app.get_chat(chat_id)

await chat.send_message("Hello!")

await chat.leave()
```

بسته به API و سطح دسترسی، عملیات مربوط به چت می‌تواند شامل موارد زیر باشد:

```python
await app.ban_chat_member(chat_id, user_id)
await app.unban_chat_member(chat_id, user_id)
await app.leave_chat(chat_id)
await app.pin_chat_message(chat_id, message_id)
```

## Callback Queries

Nicotin از Handlerهای مربوط به Callback Query پشتیبانی می‌کند:

```python
@app.on_callback_query()
async def callback(client, query):
    await query.answer("Button clicked!")
```

## فایل‌های Session

Nicotin می‌تواند اطلاعات احراز هویت را در یک فایل Session ذخیره کند.

مثال:

```python
app = Client(
    "my_account",
    auth="YOUR_AUTH_KEY"
)
```

Session با استفاده از نام Client ذخیره می‌شود:

```text
my_account.session
```

### امنیت

هرگز کلیدهای احراز هویت یا فایل‌های Session را در GitHub قرار ندهید.

فایل‌های Session و فایل‌های محیطی خود را به `.gitignore` اضافه کنید.

## بروزرسانی Nicotin

برای ارتقا به آخرین نسخه:

```bash
pip install --upgrade nicotin
```

یا:

```bash
pip install -U nicotin
```

پس از انتشار نسخه جدید در PyPI، کاربران می‌توانند با این دستور آخرین نسخه را دریافت کنند.

## نسخه فعلی

```text
0.1.0
```

آخرین نسخه منتشرشده در PyPI در دسترس است:

https://pypi.org/project/nicotin/

## توسعه

Repository را Clone کنید:

```bash
git clone https://github.com/YOUR_USERNAME/nicotin.git
cd nicotin
```

یک Virtual Environment بسازید:

```bash
python -m venv .venv
```

فعال‌سازی در Windows:

```powershell
.venv\Scripts\Activate.ps1
```

نصب پکیج در حالت Editable:

```bash
pip install -e .
```

## ساختار پروژه

```text
nicotin/
├── nicotin/
│   ├── __init__.py
│   ├── client.py
│   ├── enums/
│   ├── errors/
│   ├── filters.py
│   ├── handlers/
│   ├── network/
│   └── types/
├── tests/
├── README.md
├── LICENSE
├── .gitignore
└── pyproject.toml
```

## مشارکت

مشارکت‌ها، گزارش باگ، پیشنهاد قابلیت‌های جدید و بهبود پروژه مورد استقبال هستند.

قبل از ارسال Pull Request:

1. تغییرات را محدود و متمرکز نگه دارید.
2. سبک موجود پروژه را رعایت کنید.
3. در صورت نیاز Test اضافه کنید.
4. هنگام تغییر رفتار پروژه، مستندات را نیز بروزرسانی کنید.

## لایسنس

Nicotin تحت لایسنس MIT منتشر شده است.

برای متن کامل لایسنس به فایل [`LICENSE`](https://chatgpt.com/c/LICENSE) مراجعه کنید.

## سلب مسئولیت

Nicotin یک پروژه مستقل و Open Source است.

این پروژه به روبیکا یا مالکین آن وابسته نیست و توسط آن‌ها تأیید یا حمایت نمی‌شود.

## لینک‌ها

* PyPI: https://pypi.org/project/nicotin/
* GitHub: https://github.com/YOUR_USERNAME/nicotin

---

**Nicotin — یک کتابخانه Async پایتون برای روبیکا.**
