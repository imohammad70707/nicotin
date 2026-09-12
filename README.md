# 🚀 NICOTIN

**NICOTIN** is an asynchronous Python library for building **Rubika bots** using the **Rubika Bot API**.

Inspired by the structure and developer experience of popular libraries such as **Pyrogram**, NICOTIN is designed to make the transition for Telegram/Pyrogram developers as simple as possible when building bots for Rubika.

> ⚡ Simple, Async, and developer-friendly Python library for Rubika bots.

[🇬🇧 English](#-english) | [🇮🇷 فارسی](#-فارسی)

---

# 🇬🇧 English

## ✨ Features

* ⚡ Fully asynchronous architecture
* 🤖 Bot Token authentication
* 🔌 Rubika Bot API integration
* 🎯 Powerful filter system
* 🔗 Filter composition using `&`, `|`, and `~`
* 🧩 Handler-based event system
* 💬 Message management
* 📸 Media receiving and downloading
* 🔘 Callback Query support
* ✏️ Message editing and deletion
* 🔄 Message forwarding
* 💾 Chat information and history retrieval
* 🌐 Webhook support
* 🛡️ Dedicated error management system
* 📋 Connection and runtime logging
* 🧱 Modular and extensible architecture
* 📦 Ready to be distributed as a Python package

---

## 📦 Installation

### Install from PyPI

```bash
pip install nicotin
```

### Install the development version from source

```bash
git clone https://github.com/imohammad70707/nicotin.git
cd nicotin
pip install -e .
```

---

## 🔑 Getting a Bot Token

Before using NICOTIN, you need to obtain a **Bot Token** from Rubika.

1. Open Rubika.
2. Open the `@rubika_bot` bot.
3. Create a new bot.
4. Copy the generated Bot Token.
5. Pass the token when creating the `Client`.

> 🔐 **Never publish your Bot Token in public source code, GitHub repositories, or distributable files.**

---

## ⚡ Quick Start

A simple Rubika bot example:

```python
from nicotin import Client, filters

app = Client(bot_token="YOUR_BOT_TOKEN_HERE")


@app.on_message(filters.command("start"))
async def start(client: Client, message):
    await message.reply("سلام از نیکوتین 👋")


@app.on_message(filters.text & ~filters.command(["start", "help"]))
async def echo(client: Client, message):
    await message.reply(message.text)


@app.on_message(filters.photo)
async def on_photo(client: Client, message):
    path = await message.download()
    await message.reply(f"عکس دریافت شد و در {path} ذخیره شد.")


@app.on_callback_query()
async def on_button(client: Client, callback_query):
    await callback_query.answer("دکمه دریافت شد ✅")


if __name__ == "__main__":
    app.run()
```

Run the example:

```bash
python examples/echo_bot.py
```

---

## 🖥️ Runtime Status

While the bot is running, NICOTIN displays connection status and important runtime errors in the terminal:

```text
[NICOTIN] 14:02:10 INFO: در حال اتصال به Rubika Bot API ...
[NICOTIN] 14:02:11 INFO: ربات @your_bot با موفقیت متصل شد ✅ (0.83s) — شروع دریافت پیام‌ها ...
```

If a problem occurs with the Bot Token, network connection, timeout, request limits, or a handler, the error is logged so that problems can be diagnosed without silent failures or unexplained stops.

---

## 🎯 Filters

Filters are one of the core components of NICOTIN.

```python
filters.text
filters.photo
filters.command("start")
```

Filters can be combined using logical operators.

### AND

```python
filters.text & filters.photo
```

### OR

```python
filters.photo | filters.video
```

### NOT

```python
~filters.command(["start", "help"])
```

For example:

```python
filters.text & ~filters.command(["start", "help"])
```

This filter architecture is inspired by the design patterns used by well-known Python bot development libraries.

---

## 🧩 Handlers

Handlers provide a simple way to register different bot events.

### Message Handler

```python
@app.on_message(...)
async def handler(client, message):
    ...
```

### Callback Query Handler

```python
@app.on_callback_query()
async def callback(client, callback_query):
    ...
```

---

## 📚 API Overview

| NICOTIN                      | Pyrogram-style             | Purpose                   |
| ---------------------------- | -------------------------- | ------------------------- |
| `Client(bot_token=...)`      | `Client(...)`              | Create a client           |
| `app.run()`                  | `app.run()`                | Run the bot               |
| `Client.get_me()`            | `get_me()`                 | Get bot information       |
| `Client.send_message()`      | `send_message()`           | Send a message            |
| `Client.send_photo()`        | `send_photo()`             | Send a photo              |
| `Client.send_video()`        | `send_video()`             | Send a video              |
| `Client.send_document()`     | `send_document()`          | Send a file               |
| `Client.edit_message_text()` | `edit_message_text()`      | Edit a message            |
| `Client.delete_messages()`   | `delete_messages()`        | Delete messages           |
| `Client.forward_messages()`  | `forward_messages()`       | Forward messages          |
| `Client.get_chat()`          | `get_chat()`               | Get chat information      |
| `Client.get_chat_history()`  | `get_chat_history()`       | Get chat history          |
| `Client.set_webhook()`       | `set_webhook()`            | Configure webhook         |
| `message.reply()`            | `message.reply()`          | Reply to a message        |
| `message.edit_text()`        | `message.edit_text()`      | Edit a message            |
| `message.delete()`           | `message.delete()`         | Delete a message          |
| `filters.text`               | `filters.text`             | Text message filter       |
| `filters.photo`              | `filters.photo`            | Photo filter              |
| `filters.command()`          | `filters.command()`        | Command filter            |
| `@app.on_message()`          | `@app.on_message()`        | Register message handler  |
| `@app.on_callback_query()`   | `@app.on_callback_query()` | Register callback handler |

---

## 🛡️ Error Handling

NICOTIN provides a dedicated exception system based around `NicotinError`.

| Error              | Description                            |
| ------------------ | -------------------------------------- |
| `AuthError`        | Empty or invalid Bot Token             |
| `RPCError`         | Non-OK response from the Rubika server |
| `FloodWait`        | Request rate limit has been reached    |
| `ConnectionError_` | Network connection failure             |
| `RequestTimeout`   | Request took too long to complete      |

### Example

```python
from nicotin.errors import AuthError

try:
    ...
except AuthError:
    print("Invalid bot token.")
```

---

## 🏗️ Project Structure

```text
nicotin/
├── pyproject.toml
├── README.md
├── LICENSE
├── examples/
│   └── echo_bot.py
│
└── nicotin/
    ├── __init__.py
    ├── client.py
    ├── filters.py
    │
    ├── types/
    │   ├── __init__.py
    │   ├── object.py
    │   ├── message.py
    │   ├── user.py
    │   ├── chat.py
    │   ├── file.py
    │   ├── callback_query.py
    │   └── update.py
    │
    ├── handlers/
    │   └── __init__.py
    │
    ├── network/
    │   ├── __init__.py
    │   └── session.py
    │
    ├── errors/
    │   └── __init__.py
    │
    └── enums/
        └── __init__.py
```

---

## 🔄 Development Journey

During development, NICOTIN evolved from a **session-based personal-account authentication architecture** into a **Bot Token-based architecture using the Rubika Bot API**.

Major development milestones include:

* 🧱 Core `Client` architecture was created.
* 📦 Core types such as `Message`, `User`, `Chat`, `File`, `CallbackQuery`, and `Update` were introduced.
* 🎯 Filters and Handlers were implemented.
* 🌐 A dedicated network layer for the Bot API was created.
* 🛡️ A dedicated error system was added.
* 📋 Connection and runtime logging were developed.
* 🔐 Personal-account session authentication was removed.
* 🔌 Network communication was migrated to the JSON-based Bot API structure.

---

## 🧰 Requirements

* Python **3.10+**
* `httpx`

Project dependencies are installed automatically through the package configuration.

---

## 📄 License

NICOTIN is released under the **MIT License**.

See the [`LICENSE`](LICENSE) file for the full license text.

---

## 👨‍💻 Developer

**NICOTIN**

Built to make developing Rubika bots with Python simpler, cleaner, and more accessible.

---

## ⭐ Support the Project

If NICOTIN is useful to you, consider giving the repository a ⭐ on GitHub.

Every star helps support the continued development of the project.

**Happy Coding 🚀**

---

# 🇮🇷 فارسی

## 🚀 معرفی

**NICOTIN** یک کتابخانه‌ی Python مبتنی بر `asyncio` برای ساخت **ربات‌های روبیکا** با استفاده از **Rubika Bot API** است.

این کتابخانه با الهام از ساختار و تجربه‌ی کتابخانه‌های محبوبی مانند **Pyrogram** طراحی شده است تا توسعه‌دهندگانی که قبلاً با ساخت ربات‌های تلگرام کار کرده‌اند، بتوانند با کمترین تغییر ذهنی، ربات‌های خود را برای روبیکا توسعه دهند.

> ⚡ ساده، Async و مناسب توسعه‌ی ربات‌های روبیکا با Python

---

## ✨ ویژگی‌ها

* ⚡ معماری کاملاً Async
* 🤖 احراز هویت با Bot Token
* 🔌 ارتباط با Rubika Bot API
* 🎯 سیستم قدرتمند Filters
* 🔗 امکان ترکیب فیلترها با `&`، `|` و `~`
* 🧩 سیستم Handlers
* 💬 مدیریت پیام‌ها
* 📸 دریافت و دانلود رسانه
* 🔘 پشتیبانی از Callback Query
* ✏️ ویرایش و حذف پیام‌ها
* 🔄 فوروارد پیام‌ها
* 💾 دریافت اطلاعات چت و تاریخچه
* 🌐 پشتیبانی از Webhook
* 🛡️ سیستم مدیریت خطای اختصاصی
* 📋 لاگ‌گذاری و نمایش وضعیت اتصال
* 🧱 ساختار ماژولار و قابل توسعه
* 📦 آماده برای انتشار و نصب به‌صورت Python Package

---

## 📦 نصب

### نصب از PyPI

```bash
pip install nicotin
```

### نصب نسخه توسعه از سورس

```bash
git clone https://github.com/imohammad70707/nicotin.git
cd nicotin
pip install -e .
```

---

## 🔑 دریافت Bot Token

برای استفاده از NICOTIN ابتدا باید یک **Bot Token** از روبیکا دریافت کنید.

1. وارد روبیکا شوید.
2. ربات `@rubika_bot` را باز کنید.
3. یک Bot جدید ایجاد کنید.
4. Token دریافت‌شده را کپی کنید.
5. هنگام ساخت `Client` آن را به کتابخانه بدهید.

> 🔐 **توکن بات را هرگز در کد عمومی، GitHub یا فایل‌های قابل انتشار قرار ندهید.**

---

## ⚡ شروع سریع

یک نمونه‌ی ساده از ربات:

```python
from nicotin import Client, filters

app = Client(bot_token="YOUR_BOT_TOKEN_HERE")


@app.on_message(filters.command("start"))
async def start(client: Client, message):
    await message.reply("سلام از نیکوتین 👋")


@app.on_message(filters.text & ~filters.command(["start", "help"]))
async def echo(client: Client, message):
    await message.reply(message.text)


@app.on_message(filters.photo)
async def on_photo(client: Client, message):
    path = await message.download()
    await message.reply(f"عکس دریافت شد و در {path} ذخیره شد.")


@app.on_callback_query()
async def on_button(client: Client, callback_query):
    await callback_query.answer("دکمه دریافت شد ✅")


if __name__ == "__main__":
    app.run()
```

سپس اجرا کنید:

```bash
python examples/echo_bot.py
```

---

## 🖥️ وضعیت اجرا

NICOTIN هنگام اجرای ربات، وضعیت اتصال و خطاهای مهم را در ترمینال نمایش می‌دهد:

```text
[NICOTIN] 14:02:10 INFO: در حال اتصال به Rubika Bot API ...
[NICOTIN] 14:02:11 INFO: ربات @your_bot با موفقیت متصل شد ✅ (0.83s) — شروع دریافت پیام‌ها ...
```

در صورت وجود مشکل در Token، اتصال شبکه، Timeout، محدودیت درخواست یا خطا داخل Handler، اطلاعات خطا در لاگ ثبت می‌شود تا مشکل بدون توقف نامشخص و خطای خاموش قابل پیگیری باشد.

---

## 🎯 Filters

فیلترها یکی از بخش‌های اصلی NICOTIN هستند و می‌توان آن‌ها را با عملگرهای منطقی ترکیب کرد:

```python
filters.text
filters.photo
filters.command("start")
```

### ترکیب با AND

```python
filters.text & filters.photo
```

### ترکیب با OR

```python
filters.photo | filters.video
```

### ترکیب با NOT

```python
~filters.command(["start", "help"])
```

برای مثال:

```python
filters.text & ~filters.command(["start", "help"])
```

این ساختار با الهام از الگوهای رایج در کتابخانه‌های Python برای توسعه‌ی ربات طراحی شده است.

---

## 🧩 Handlers

ثبت Handler برای رویدادهای مختلف به شکل ساده انجام می‌شود:

```python
@app.on_message(...)
async def handler(client, message):
    ...
```

برای Callback Query نیز:

```python
@app.on_callback_query()
async def callback(client, callback_query):
    ...
```

---

## 📚 نمای کلی API

| NICOTIN                      | سبک Pyrogram               | کاربرد               |
| ---------------------------- | -------------------------- | -------------------- |
| `Client(bot_token=...)`      | `Client(...)`              | ساخت Client          |
| `app.run()`                  | `app.run()`                | اجرای ربات           |
| `Client.get_me()`            | `get_me()`                 | دریافت اطلاعات بات   |
| `Client.send_message()`      | `send_message()`           | ارسال پیام           |
| `Client.send_photo()`        | `send_photo()`             | ارسال عکس            |
| `Client.send_video()`        | `send_video()`             | ارسال ویدیو          |
| `Client.send_document()`     | `send_document()`          | ارسال فایل           |
| `Client.edit_message_text()` | `edit_message_text()`      | ویرایش پیام          |
| `Client.delete_messages()`   | `delete_messages()`        | حذف پیام             |
| `Client.forward_messages()`  | `forward_messages()`       | فوروارد پیام         |
| `Client.get_chat()`          | `get_chat()`               | دریافت اطلاعات چت    |
| `Client.get_chat_history()`  | `get_chat_history()`       | دریافت تاریخچه چت    |
| `Client.set_webhook()`       | `set_webhook()`            | تنظیم Webhook        |
| `message.reply()`            | `message.reply()`          | پاسخ به پیام         |
| `message.edit_text()`        | `message.edit_text()`      | ویرایش پیام          |
| `message.delete()`           | `message.delete()`         | حذف پیام             |
| `filters.text`               | `filters.text`             | فیلتر پیام متنی      |
| `filters.photo`              | `filters.photo`            | فیلتر عکس            |
| `filters.command()`          | `filters.command()`        | فیلتر دستورات        |
| `@app.on_message()`          | `@app.on_message()`        | ثبت Handler پیام     |
| `@app.on_callback_query()`   | `@app.on_callback_query()` | ثبت Callback Handler |

---

## 🛡️ مدیریت خطا

NICOTIN دارای سیستم خطای اختصاصی است و خطاهای مختلف را از `NicotinError` مدیریت می‌کند.

| خطا                | توضیح                              |
| ------------------ | ---------------------------------- |
| `AuthError`        | Token خالی یا نامعتبر              |
| `RPCError`         | دریافت وضعیت غیر OK از سرور روبیکا |
| `FloodWait`        | اعمال محدودیت نرخ درخواست          |
| `ConnectionError_` | برقرار نشدن اتصال شبکه             |
| `RequestTimeout`   | طولانی شدن بیش از حد درخواست       |

### نمونه

```python
from nicotin.errors import AuthError

try:
    ...
except AuthError:
    print("Bot token نامعتبر است.")
```

---

## 🏗️ ساختار پروژه

```text
nicotin/
├── pyproject.toml
├── README.md
├── LICENSE
├── examples/
│   └── echo_bot.py
│
└── nicotin/
    ├── __init__.py
    ├── client.py
    ├── filters.py
    │
    ├── types/
    │   ├── __init__.py
    │   ├── object.py
    │   ├── message.py
    │   ├── user.py
    │   ├── chat.py
    │   ├── file.py
    │   ├── callback_query.py
    │   └── update.py
    │
    ├── handlers/
    │   └── __init__.py
    │
    ├── network/
    │   ├── __init__.py
    │   └── session.py
    │
    ├── errors/
    │   └── __init__.py
    │
    └── enums/
        └── __init__.py
```

---

## 🔄 مسیر توسعه

NICOTIN در طول توسعه از یک ساختار مبتنی بر **Session و احراز هویت حساب شخصی** به معماری مبتنی بر **Bot Token و Rubika Bot API** منتقل شده است.

در این مسیر:

* 🧱 ساختار اصلی `Client` ایجاد شد.
* 📦 Typeهای اصلی مانند `Message`، `User`، `Chat`، `File`، `CallbackQuery` و `Update` اضافه شدند.
* 🎯 سیستم Filters و Handlers پیاده‌سازی شد.
* 🌐 لایه‌ی شبکه برای Bot API ایجاد شد.
* 🛡️ سیستم خطای اختصاصی اضافه شد.
* 📋 لاگ‌های اتصال و خطا توسعه داده شدند.
* 🔐 وابستگی به Session و ورود با حساب شخصی حذف شد.
* 🔌 ارتباط شبکه به ساختار JSON مربوط به Bot API منتقل شد.

---

## 🧰 نیازمندی‌ها

* Python **3.10 یا بالاتر**
* `httpx`

وابستگی‌های پروژه از طریق تنظیمات Package نصب می‌شوند.

---

## 📄 مجوز

این پروژه تحت **MIT License** منتشر شده است.

برای جزئیات کامل، فایل [`LICENSE`](LICENSE) را مطالعه کنید.

---

## 👨‍💻 توسعه‌دهنده

**NICOTIN**

ساخته‌شده برای ساده‌تر، تمیزتر و قابل‌دسترس‌تر کردن توسعه‌ی ربات‌های روبیکا با Python.

---

## ⭐ حمایت از پروژه

اگر NICOTIN برای شما مفید است، می‌توانید با ⭐ دادن به Repository پروژه در GitHub از توسعه‌ی آن حمایت کنید.

هر ⭐ می‌تواند به ادامه‌ی توسعه‌ی پروژه کمک کند.

**Happy Coding 🚀**
