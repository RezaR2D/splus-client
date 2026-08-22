# SPlus Bot Core

هسته اتوماسیون و ساخت ربات پیام‌رسان برای **سروش پلاس** ([web.splus.ir](https://web.splus.ir))

این پروژه یک لایه آماده برای ساخت ربات پاسخگوی خودکار است. با استفاده از آن می‌توانید پیام‌ها را دریافت کنید، پاسخ دهید، فایل ارسال کنید و عملیات رایج مدیریت پیام را انجام دهید.

**توسعه‌دهنده:** رضا منفرد  
**گیت‌هاب:** [https://github.com/RezaR2D](https://github.com/RezaR2D)

---

## کاربرد

مناسب برای ساخت:

- ربات پاسخگوی خودکار
- ربات پشتیبانی
- ربات اطلاع‌رسان
- ابزارهای اتوماسیون پیام در سروش پلاس

به‌جای شروع از صفر، این هسته اتصال، سشن، ارسال و دریافت را فراهم می‌کند و شما فقط منطق ربات را می‌نویسید.

---

## قابلیت‌ها

- ورود و ذخیره نشست کاربری
- دریافت لحظه‌ای پیام‌های جدید
- ارسال پیام متنی و پاسخ (Reply)
- ارسال فایل از سیستم یا لینک
- پین و آن‌پین پیام
- حذف پیام
- فیلتر پیام‌های خود ربات
- قابل توسعه برای هر سناریوی اتوماسیون

---

## نصب

پیش‌نیازها: Python 3.10+ و Google Chrome

```bash
git clone https://github.com/RezaR2D/splus-client.git
cd splus-client
python setup.py
```

یا:

```bash
pip install -r requirements.txt
```

---

## اجرا

```bash
python main.py
```

در اجرای اول، اگر نشست ذخیره نشده باشد فرایند ورود انجام می‌شود و فایل نشست ساخته می‌شود. اجراهای بعدی معمولاً بدون ورود مجدد انجام می‌گیرد.

فایل نشست مخصوص هر کاربر است و نباید در مخزن قرار بگیرد.

برای توقف دریافت پیام، در ترمینال بنویسید:

```text
exit
```

---

## ساخت ربات پاسخگو

منطق ربات داخل تابع handler نوشته می‌شود:

```python
def on_new_message(update, chat_id, message_id):
    text = (
        update.get("message", {})
        .get("content", {})
        .get("text", {})
        .get("text", "")
    )

    client.send_message(
        chat_id=chat_id,
        text=f"پیام شما دریافت شد: {text}",
        reply_to=message_id
    )

client.listen_for_updates(
    handler=on_new_message,
    self_messages=False,
    poll_interval=0.35
)
```

---

## مرجع کامل متدها

### ارسال پیام — send_message

```python
client.send_message(
    chat_id="123456",
    text="سلام",
    thread_id=-1,
    is_silent=False,
    reply_to=None
)
```

| پارامتر | پیش‌فرض | توضیح |
|--------|---------|--------|
| chat_id | — | شناسه چت مقصد |
| text | — | متن پیام |
| reply_to | None | شناسه پیام برای پاسخ (ریپلای) |
| is_silent | False | ارسال بی‌صدا |
| thread_id | -1 | شناسه ترد |

مثال ساده:

```python
client.send_message(chat_id="123456", text="سلام")
```

پاسخ به پیام:

```python
client.send_message(
    chat_id="123456",
    text="پیام شما دریافت شد",
    reply_to=189
)
```

---

### ارسال فایل — send_file

```python
client.send_file(
    chat_id="123456",
    source="path_or_url",
    thread_id=-1,
    caption="",
    is_silent=False,
    reply_to=None
)
```

| پارامتر | پیش‌فرض | توضیح |
|--------|---------|--------|
| chat_id | — | شناسه چت |
| source | — | مسیر فایل روی سیستم یا لینک مستقیم |
| caption | "" | زیرنویس فایل |
| reply_to | None | پاسخ به پیام |
| is_silent | False | ارسال بی‌صدا |
| thread_id | -1 | شناسه ترد |

از سیستم:

```python
client.send_file(
    chat_id="123456",
    source=r"C:\files\photo.jpg",
    caption="ارسال از سیستم"
)
```

از لینک:

```python
client.send_file(
    chat_id="123456",
    source="https://example.com/image.jpg",
    caption="ارسال از لینک"
)
```

با پاسخ:

```python
client.send_file(
    chat_id="123456",
    source="report.pdf",
    caption="گزارش",
    reply_to=189
)
```

اگر source با http:// یا https:// شروع شود، فایل ابتدا دانلود و سپس ارسال می‌شود. در غیر این صورت به‌عنوان مسیر محلی خوانده می‌شود.

میان‌بر کپشن‌دار:

```python
client.send_file_with_caption(
    chat_id="123456",
    source="photo.jpg",
    caption="توضیح فایل"
)
```

---

### پین پیام — pin_message

```python
client.pin_message(
    chat_id="123456",
    message_id=189,
    one_side=False,
    silent=False,
    open_chat=True
)
```

| پارامتر | پیش‌فرض | توضیح |
|--------|---------|--------|
| chat_id | — | شناسه چت |
| message_id | — | یک آیدی یا لیست آیدی‌ها |
| one_side | False | پین فقط برای خود کاربر |
| silent | False | پین بدون اعلان |
| open_chat | True | باز کردن چت قبل از پین |

مثال‌ها:

```python
client.pin_message("123456", 189)
client.pin_message("123456", [189, 190])
client.pin_message("123456", 189, one_side=True)
```

---

### آن‌پین پیام — unpin_message

```python
client.unpin_message(
    chat_id="123456",
    message_id=189,
    open_chat=True
)
```

| پارامتر | پیش‌فرض | توضیح |
|--------|---------|--------|
| chat_id | — | شناسه چت |
| message_id | — | یک آیدی یا لیست آیدی‌ها |
| open_chat | True | باز کردن چت قبل از عملیات |

مثال‌ها:

```python
client.unpin_message("123456", 189)
client.unpin_message("123456", [189, 190])
```

---

### حذف پیام — delete_message

```python
client.delete_message(
    chat_id="123456",
    message_id=189,
    for_all=False,
    open_chat=True
)
```

| پارامتر | پیش‌فرض | توضیح |
|--------|---------|--------|
| chat_id | — | شناسه چت |
| message_id | — | یک آیدی یا لیست آیدی‌ها |
| for_all | False | حذف فقط برای خود / برای همه |
| open_chat | True | باز کردن چت قبل از حذف |

مثال‌ها:

```python
client.delete_message("123456", 189)
client.delete_message("123456", 189, for_all=True)
client.delete_message("123456", [189, 190, 191])
```

---

### دریافت پیام‌های جدید — listen_for_updates

```python
client.listen_for_updates(
    handler=on_new_message,
    self_messages=False,
    poll_interval=0.35
)
```

| پارامتر | پیش‌فرض | توضیح |
|--------|---------|--------|
| handler | — | تابع پردازش هر پیام جدید |
| self_messages | False | نادیده گرفتن پیام‌های خود ربات |
| poll_interval | 0.35 | فاصله بررسی پیام‌های جدید (ثانیه) |

امضای handler:

```python
def on_new_message(update, chat_id, message_id):
    ...
```

- update : کل داده پیام
- chat_id : شناسه چت
- message_id : شناسه پیام

خواندن متن پیام:

```python
text = (
    update.get("message", {})
    .get("content", {})
    .get("text", {})
    .get("text", "")
)
```

اگر پیام متنی نباشد (عکس، ویدیو، فایل و ...)، ممکن است content.text وجود نداشته باشد.

---

## مثال ربات ساده

```python
def on_new_message(update, chat_id, message_id):
    text = (
        update.get("message", {})
        .get("content", {})
        .get("text", {})
        .get("text", "")
        .strip()
        .lower()
    )

    if text == "سلام":
        client.send_message(chat_id, "سلام، خوش آمدید", reply_to=message_id)

    elif text == "راهنما":
        client.send_message(
            chat_id,
            "دستورات: سلام | راهنما | فایل",
            reply_to=message_id
        )

    elif text == "فایل":
        client.send_file(
            chat_id=chat_id,
            source="https://example.com/help.png",
            caption="فایل راهنما",
            reply_to=message_id
        )

    elif text == "پین":
        client.pin_message(chat_id, message_id)

    elif text == "حذف":
        client.delete_message(chat_id, message_id)

client.listen_for_updates(handler=on_new_message, self_messages=False)
```

---

## ساختار پروژه

```text
setup.py            نصب پیش‌نیازها
main.py             نمونه اجرا و ربات
login.py            ورود و ذخیره نشست
splus_client.py     هسته اصلی
requirements.txt    وابستگی‌ها
README.md           راهنما
.gitignore          نادیده گرفتن فایل‌های حساس و موقت
```

---

## نکات مهم

- این ابزار بر پایه نسخه وب سروش پلاس و Selenium کار می‌کند و API رسمی عمومی نیست.
- با تغییر ساختار وب‌اپ، ممکن است نیاز به به‌روزرسانی باشد.
- از ارسال انبوه ناخواسته و استفاده خلاف قوانین سرویس خودداری کنید.
- مسئولیت استفاده بر عهده کاربر است.
- فایل نشست را مانند اطلاعات ورود محرمانه نگه دارید.
- برای پین، آن‌پین و حذف در اتوماسیون، باز شدن چت (open_chat=True) معمولاً لازم است.

---

## نویسنده

رضا منفرد  
https://github.com/RezaR2D
