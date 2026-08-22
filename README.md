# SPlus Client

یک هسته آماده اتوماسیون برای توسعه ربات‌های پیام‌رسان داخلی **سروش پلاس (SPlus)** با زبان Python و Selenium.

`SPlus Client` به‌عنوان یک کتابخانه طراحی شده تا توسعه‌دهنده بدون درگیر شدن با جزئیات ارتباط با نسخه وب سروش پلاس، بتواند ربات و برنامه موردنظر خود را توسعه دهد.

> ⚠️ این پروژه API رسمی سروش پلاس نیست و برای ارتباط با نسخه وب SPlus از Selenium استفاده می‌کند.

---

## ✨ امکانات

* 🤖 هسته آماده برای توسعه ربات سروش پلاس
* 🔐 ورود خودکار به حساب
* 💾 مدیریت و ذخیره Session
* 📥 دریافت پیام‌های جدید
* 🎯 دریافت `chat_id` و `message_id`
* 💬 ارسال پیام
* ↩️ پاسخ مستقیم به پیام
* 📌 سنجاق کردن پیام
* 🔄 دریافت مداوم Updateها
* 🎛️ سیستم Handler با `@client.on_message`
* ⚙️ کنترل Client با `run()` و `close()`
* 🐍 قابل استفاده به‌عنوان Python Library
* 🚀 مناسب برای توسعه پروژه‌های مستقل بر پایه SPlus

---

## 📦 نصب

پس از انتشار در PyPI، کتابخانه را با دستور زیر نصب کنید:

```bash
pip install splus-client
```

برای بروزرسانی:

```bash
pip install -U splus-client
```

---

## 🚀 شروع سریع

پس از نصب، کتابخانه را Import کنید:

```python
from splus_client import SPlusClient
```

Client را ایجاد کنید:

```python
client = SPlusClient(display_logs=True)
```

فرآیند ورود به حساب توسط کتابخانه به‌صورت خودکار انجام می‌شود و نیازی نیست فرآیند Login را به‌صورت دستی در کد ربات پیاده‌سازی کنید.

---

# 📥 دریافت پیام

برای دریافت پیام‌های جدید از Decorator زیر استفاده کنید:

```python
@client.on_message
```

Handler مربوط به پیام سه مقدار دریافت می‌کند:

```python
@client.on_message
def on_new_message(update, chat_id, message_id):
    print("پیام جدید دریافت شد")
    print("chat_id:", chat_id)
    print("message_id:", message_id)
    print("update:", update)
```

پس از تعریف Handler، دریافت پیام‌ها با `run()` شروع می‌شود:

```python
client.run(
    include_self=False,
    poll_interval=0.35
)
```

---

## 🔹 پارامترهای Handler

تابع Handler به شکل زیر است:

```python
def on_new_message(update, chat_id, message_id):
    ...
```

### `update`

اطلاعات کامل Update دریافت‌شده.

```python
print(update)
```

### `chat_id`

شناسه چتی که پیام در آن دریافت شده است.

```python
print(chat_id)
```

### `message_id`

شناسه پیام دریافت‌شده.

```python
print(message_id)
```

از `message_id` می‌توان برای پاسخ دادن یا سنجاق کردن پیام استفاده کرد.

---

# 📝 دریافت متن پیام

ساختار متن پیام در Update قرار دارد.

برای دریافت متن:

```python
text = str(
    update.get("message", {})
          .get("content", {})
          .get("text", {})
          .get("text", "")
)
```

مثال:

```python
@client.on_message
def on_new_message(update, chat_id, message_id):

    text = str(
        update.get("message", {})
              .get("content", {})
              .get("text", {})
              .get("text", "")
    )

    print("پیام:", text)
```

---

# 💬 ارسال پیام

برای ارسال پیام از `send_message()` استفاده کنید:

```python
client.send_message(
    chat_id="CHAT_ID",
    text="سلام!"
)
```

مثال:

```python
client.send_message(
    chat_id="123456789",
    text="سلام، این پیام توسط ربات ارسال شده است."
)
```

---

# ↩️ پاسخ به پیام

با استفاده از `reply_to` می‌توانید پیام را به‌صورت Reply ارسال کنید:

```python
client.send_message(
    chat_id=chat_id,
    text="پیامت دریافت شد!",
    reply_to=message_id
)
```

مثال کامل:

```python
@client.on_message
def on_new_message(update, chat_id, message_id):

    client.send_message(
        chat_id=chat_id,
        text="سلام! پیامت دریافت شد.",
        reply_to=message_id
    )
```

---

# 📌 سنجاق کردن پیام

برای سنجاق کردن پیام:

```python
client.pin_message(
    chat_id,
    message_id
)
```

مثال:

```python
@client.on_message
def on_new_message(update, chat_id, message_id):

    client.pin_message(
        chat_id,
        message_id
    )
```

---

# 🤖 ساخت یک ربات ساده

نمونه زیر یک ربات ساده است که پیام دریافت می‌کند، متن آن را استخراج می‌کند و به همان پیام پاسخ می‌دهد:

```python
from splus_client import SPlusClient


client = SPlusClient(display_logs=True)


@client.on_message
def on_new_message(update, chat_id, message_id):

    text = str(
        update.get("message", {})
              .get("content", {})
              .get("text", {})
              .get("text", "")
    )

    print("📩 پیام:", text)

    client.send_message(
        chat_id=chat_id,
        text="سلام! تو گفتی: " + text,
        reply_to=message_id
    )


client.run(
    include_self=False,
    poll_interval=0.35
)
```

---

# ⚙️ اجرای Client

برای شروع دریافت پیام‌ها:

```python
client.run(
    include_self=False,
    poll_interval=0.35
)
```

## `include_self`

تعیین می‌کند پیام‌های ارسال‌شده توسط خود حساب نیز به Handler ارسال شوند یا خیر.

### غیرفعال کردن پیام‌های خود حساب

```python
include_self=False
```

این حالت برای اکثر ربات‌ها مناسب است.

### دریافت پیام‌های خود حساب

```python
include_self=True
```

---

## `poll_interval`

فاصله بررسی Updateهای جدید را مشخص می‌کند.

مثلاً:

```python
poll_interval=0.35
```

مقدار کمتر باعث بررسی مکررتر Updateها می‌شود.

---

# 🧹 بستن Client

پس از پایان کار، Client را ببندید:

```python
client.close()
```

بهتر است از `try/finally` استفاده شود:

```python
from splus_client import SPlusClient


client = SPlusClient(display_logs=True)

try:

    @client.on_message
    def on_new_message(update, chat_id, message_id):
        print("پیام جدید:", chat_id, message_id)

    client.run(
        include_self=False,
        poll_interval=0.35
    )

finally:
    client.close()
```

---

# 🔐 ورود خودکار

یکی از اهداف اصلی `SPlus Client` ساده کردن فرآیند ورود است.

توسعه‌دهنده نیازی به پیاده‌سازی دستی مراحل ورود، باز کردن صفحه Login یا مدیریت فرآیند احراز هویت در کد ربات ندارد.

کافی است Client را ایجاد کنید:

```python
client = SPlusClient()
```

کتابخانه فرآیند موردنیاز برای ورود را مدیریت می‌کند.

پس از ورود موفق، Session برای استفاده‌های بعدی مدیریت می‌شود.

> 🔒 فایل‌های Session را در اختیار دیگران قرار ندهید.

---

# 💾 Session

Session برای حفظ وضعیت ورود استفاده می‌شود.

این موضوع باعث می‌شود اجرای مجدد ربات تا حد امکان بدون نیاز به انجام دوباره فرآیند ورود انجام شود.

فایل Session نباید در GitHub یا سایر مخازن عمومی قرار گیرد.

در `.gitignore` می‌توانید Sessionها را قرار دهید:

```gitignore
*.session
```

---

# 🧩 ساختار پیشنهادی ربات

پیشنهاد می‌شود کد ربات را از کتابخانه جدا نگه دارید:

```text
my-bot/
│
├── bot.py
├── handlers/
│   ├── messages.py
│   └── commands.py
│
├── .gitignore
└── README.md
```

کتابخانه فقط وظیفه ارتباط با SPlus را برعهده دارد و منطق ربات در پروژه شما قرار می‌گیرد.

---

# 🌐 Selenium

این پروژه بر پایه **Selenium** ساخته شده و از نسخه وب SPlus برای ارتباط با سرویس استفاده می‌کند.

بنابراین برای اجرای آن به یک مرورگر Chromium-compatible نیاز است.

پیش‌نیازهای اصلی:

* Python 3.10+
* Chrome یا مرورگر Chromium-compatible
* Selenium
* Requests

وابستگی‌های Python هنگام نصب Package مدیریت خواهند شد.

---

# 📚 مثال کامل

```python
from splus_client import SPlusClient


def main():

    client = SPlusClient(display_logs=True)

    try:

        @client.on_message
        def on_new_message(update, chat_id, message_id):

            print("=" * 50)
            print("📩 پیام جدید")
            print("chat_id    →", chat_id)
            print("message_id →", message_id)
            print("update کامل:")
            print(update)
            print("=" * 50)

            text = str(
                update.get("message", {})
                      .get("content", {})
                      .get("text", {})
                      .get("text", "")
            )

            client.send_message(
                chat_id=chat_id,
                text="سلام! تو گفتی: " + text,
                reply_to=message_id
            )

            client.pin_message(
                chat_id,
                message_id
            )

        client.run(
            include_self=False,
            poll_interval=0.35
        )

    finally:
        client.close()


if __name__ == "__main__":
    main()
```

---

# 🛠️ توسعه ربات

برای توسعه ربات نیازی به تغییر سورس `SPlus Client` ندارید.

کتابخانه را نصب کنید:

```bash
pip install splus-client
```

سپس:

```python
from splus_client import SPlusClient
```

و ربات خودتان را توسعه دهید.

به این ترتیب:

```text
SPlus Client
      │
      ├── ارتباط با SPlus
      ├── Login
      ├── Session
      ├── دریافت پیام
      ├── ارسال پیام
      └── مدیریت Update
              │
              ▼
          ربات شما
              │
              ├── دستورات
              ├── منطق برنامه
              ├── دیتابیس
              └── قابلیت‌های اختصاصی
```

---

# ⚠️ نکات

* این پروژه API رسمی سروش پلاس نیست.
* ارتباط با SPlus از طریق نسخه وب و Selenium انجام می‌شود.
* تغییرات نسخه وب SPlus ممکن است باعث نیاز به بروزرسانی کتابخانه شود.
* Session حاوی اطلاعات حساس ورود است و نباید منتشر شود.
* از قرار دادن اطلاعات حساب و Session در Repository عمومی خودداری کنید.
* استفاده از این کتابخانه باید مطابق قوانین و شرایط سرویس SPlus باشد.

---

# 📄 License

این پروژه تحت مجوز **MIT License** منتشر شده است.

استفاده از کتابخانه در پروژه‌های شخصی و تجاری آزاد است و می‌توانید ربات یا برنامه خود را بر پایه آن توسعه دهید.

جزئیات کامل مجوز در فایل `LICENSE` قرار دارد.

---

# 👨‍💻 توسعه‌دهنده

ساخته شده توسط **RezaR2D**

GitHub:

https://github.com/RezaR2D

Repository:

https://github.com/RezaR2D/splus-client

---

# ⭐ حمایت از پروژه

اگر این پروژه برای شما مفید بود، با ⭐ دادن به Repository در GitHub از توسعه آن حمایت کنید.
