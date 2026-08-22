**# SPlus Client

کتابخانه پایتون برای کار با **سروش پلاس (SPlus)** از طریق نسخه وب.

این پروژه یک Client ساده برای ساخت ربات‌ها و برنامه‌های شخصی مبتنی بر SPlus فراهم می‌کند و امکاناتی مانند ورود به حساب، ارسال پیام، ارسال فایل و دریافت رویدادهای پیام را در اختیار توسعه‌دهنده قرار می‌دهد.

> ⚠️ این پروژه یک API رسمی از سروش پلاس نیست و برای کار با نسخه وب SPlus از Selenium استفاده می‌کند.

---

## ✨ امکانات

* 🔐 ورود به حساب SPlus
* 💬 ارسال پیام
* 📎 ارسال فایل
* 🖼️ ارسال تصاویر
* ↩️ ارسال پیام در پاسخ به پیام دیگر
* 📥 دریافت رویدادهای پیام
* 👤 دریافت اطلاعات کاربر فعلی
* 💾 ذخیره Session
* 🤖 مناسب برای ساخت ربات و Automation
* 🐍 قابل استفاده به‌عنوان Python Library

---

## 📦 نصب

پس از انتشار در PyPI می‌توانید کتابخانه را با دستور زیر نصب کنید:

```bash
pip install splus-client
```

برای به‌روزرسانی به آخرین نسخه:

```bash
pip install -U splus-client
```

---

## 🚀 شروع کار

پس از نصب، کتابخانه را Import کنید:

```python
from splus_client import SPlusClient
```

سپس Client را ایجاد کنید:

```python
from splus_client import SPlusClient

client = SPlusClient()
```

از اینجا می‌توانید از متدهای Client برای کار با SPlus استفاده کنید.

---

## 🔐 ورود به حساب

برای ورود، شماره تلفن حساب SPlus خود را وارد کنید:

```python
client.login("98xxxxxxxxxx")
```

در صورت نیاز، کتابخانه کد ارسال‌شده به شماره تلفن را دریافت و فرآیند ورود را انجام می‌دهد.

پس از ورود، Session ذخیره می‌شود تا در اجرای بعدی نیازی به ورود مجدد نباشد.

---

## 💬 ارسال پیام

برای ارسال پیام:

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
    text="سلام، این پیام توسط SPlus Client ارسال شده است."
)
```

---

## ↩️ پاسخ به پیام

برای ارسال پیام در پاسخ به یک پیام:

```python
client.send_message(
    chat_id="CHAT_ID",
    text="این یک پاسخ است",
    reply_to=MESSAGE_ID
)
```

---

## 📎 ارسال فایل

کتابخانه امکان ارسال فایل را نیز فراهم می‌کند:

```python
client.send_file(
    chat_id="CHAT_ID",
    file_path="example.jpg"
)
```

برای مثال:

```python
client.send_file(
    chat_id="123456789",
    file_path="photo.png"
)
```

---

 📥 دریافت پیام‌ها

می‌توانید Listener برای دریافت رویدادهای جدید ایجاد کنید:

```python
def handler(update):
    print(update)


client.listen_for_updates(handler)
```

در صورت دریافت پیام جدید، تابع `handler` اجرا خواهد شد.

---

## 🤖 ساخت ربات

هدف اصلی این کتابخانه این است که بتوانید منطق ربات خود را جدا از Client بنویسید.

برای مثال:

```python
from splus_client import SPlusClient


client = SPlusClient()


def handle_update(update):
    print(update)

    # منطق ربات شما


client.listen_for_updates(handle_update)
```

به این شکل `SPlusClient` وظیفه ارتباط با SPlus را برعهده دارد و منطق ربات کاملاً در پروژه شما قرار می‌گیرد.

---

## 📁 Session

برای جلوگیری از ورود مجدد، Session حساب در فایل Session ذخیره می‌شود.

در اجرای بعدی، در صورت معتبر بودن Session، Client می‌تواند از همان Session استفاده کند.

می‌توانید Session را در پروژه خود مدیریت کنید و در صورت نیاز آن را حذف کنید تا ورود مجدد انجام شود.

> فایل Session را در اختیار دیگران قرار ندهید؛ این فایل می‌تواند شامل اطلاعات احراز هویت حساب شما باشد.

---

## 🌐 Selenium

این کتابخانه برای ارتباط با نسخه وب SPlus از Selenium استفاده می‌کند.

بنابراین برای اجرای Client، یک مرورگر Chromium-compatible مورد نیاز است.

کتابخانه از Selenium برای کنترل مرورگر و تعامل با نسخه وب SPlus استفاده می‌کند.

---

## ⚙️ Requirements

نیازمندی‌های اصلی پروژه شامل موارد زیر هستند:

* Python 3.10+
* Selenium
* Requests
* مرورگر Chromium / Chrome

وابستگی‌های Python هنگام نصب Package توسط `pip` نصب خواهند شد.

---

## 🛠️ توسعه

اگر قصد توسعه ربات خود را دارید، کافی است کتابخانه را نصب کنید:

```bash
pip install splus-client
```

سپس در پروژه خود:

```python
from splus_client import SPlusClient
```

را استفاده کنید.

کد ربات، Handlerها و منطق برنامه باید در پروژه خودتان قرار داشته باشد و نیازی به تغییر سورس اصلی کتابخانه نیست.

---

## 📚 نمونه

یک نمونه ساده:

```python
from splus_client import SPlusClient


client = SPlusClient()


def on_update(update):
    print("New update:", update)


client.listen_for_updates(on_update)
```

نمونه‌های بیشتر در پوشه `examples` قرار خواهند گرفت.

---

## ⚠️ نکات

* این پروژه API رسمی SPlus نیست.
* عملکرد کتابخانه به نسخه وب SPlus وابسته است.
* ممکن است تغییرات نسخه وب باعث نیاز به بروزرسانی کتابخانه شود.
* Session خود را در اختیار دیگران قرار ندهید.
* استفاده از این کتابخانه باید مطابق قوانین و شرایط استفاده سرویس SPlus باشد.

---

## 📄 License

این پروژه تحت مجوز **MIT License** منتشر شده است.

شما می‌توانید از کتابخانه در پروژه‌های شخصی و تجاری خود استفاده کنید و ربات یا برنامه خود را بر پایه آن توسعه دهید.

برای جزئیات بیشتر فایل `LICENSE` را مشاهده کنید.

---

## 👨‍💻 توسعه‌دهنده

ساخته شده توسط **RezaR2D**

GitHub:

https://github.com/RezaR2D

Repository:

https://github.com/RezaR2D/splus-client

---

## ⭐ حمایت از پروژه

اگر این پروژه برای شما مفید بود، می‌توانید با ⭐ دادن به Repository در GitHub از توسعه آن حمایت کنید.
**
