import sys
import subprocess
from pathlib import Path
import importlib.util


def install_requirements():
    requirements_file = Path(__file__).parent / "requirements.txt"

    if not requirements_file.exists():
        print("❌ فایل requirements.txt پیدا نشد.")
        sys.exit(1)

    required_packages = {
        "selenium": "selenium",
        "requests": "requests"
    }

    missing_packages = []

    for package_name, import_name in required_packages.items():
        if importlib.util.find_spec(import_name) is None:
            missing_packages.append(package_name)

    if not missing_packages:
        return

    print("=" * 50)
    print("⚠️ بعضی پیش‌نیازها نصب نیستند.")
    print("📦 در حال نصب پیش‌نیازها...")
    print("=" * 50)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-r",
            str(requirements_file)
        ]
    )

    if result.returncode != 0:
        print("\n❌ نصب پیش‌نیازها ناموفق بود.")
        sys.exit(1)

    print("\n✅ پیش‌نیازها با موفقیت نصب شدند.")


install_requirements()

import os
import json
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from login import login
from splus_client import SPlusClient

"""
فایل اصلی برنامه برای مدیریت ورود و کار با سروش‌پلاس.

در صورت نصب نبودن پیش‌نیازها، آن‌ها به‌صورت خودکار
از طریق requirements.txt نصب می‌شوند.

پس از آماده شدن پیش‌نیازها، فرآیند ورود و اجرای Client
به‌صورت خودکار انجام می‌شود.

https://github.com/RezaR2D
"""
SESSION_FILE = "my.session"
LOGIN_URL = "https://web.splus.ir/"


def create_driver():
    options = Options()

    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)

    storage = {}
    if os.path.isfile(SESSION_FILE):
        with open(SESSION_FILE, "r", encoding="utf-8") as f:
            storage = json.load(f)

    storage["pwas"] = "1"
    storage_json = json.dumps(storage, ensure_ascii=False)

    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": f"""
                Object.defineProperty(navigator, 'webdriver', {{ get: () => undefined }});

                const storage = {storage_json};
                for (const [key, value] of Object.entries(storage)) {{
                    localStorage.setItem(key, String(value));
                }}
            """
        }
    )

    return driver


def wait_until_ready(driver, max_wait=90):
    print("⏳ منتظر لود کامل صفحه...")
    start = time.time()

    while time.time() - start < max_wait:
        try:
            has_floader = driver.execute_script("""
                const el = document.getElementById('floader');
                if (!el) return false;
                const style = window.getComputedStyle(el);
                return style.display !== 'none' && el.offsetParent !== null;
            """)

            if has_floader:
                print("⚠️ بارگذاری طول کشید → رفرش صفحه...")
                driver.refresh()
                time.sleep(4)
                continue

            ready = driver.execute_script("""
                return !!(
                    document.readyState === 'complete' &&
                    window.webpackChunkSoroushPlus &&
                    !document.getElementById('floader')
                );
            """)

            if ready:
                print("✅ صفحه آماده است")
                return True

        except Exception:
            pass

        time.sleep(1.5)

    print("⚠️ زمان انتظار تمام شد، ادامه می‌دهیم...")
    return False


def main():
    has_session = os.path.isfile(SESSION_FILE)
    driver = create_driver()

    try:
        driver.get(LOGIN_URL)

        if not has_session:
            print("🔐 Session not found")
            login(driver)
        else:
            print("✅ Session found")

        wait_until_ready(driver, max_wait=90)
        time.sleep(10)

        client = SPlusClient(driver, display_logs=True)

        def on_new_message(update, chat_id, message_id):
            print("=" * 50)
            print("📩 پیام جدید")
            print("chat_id   →", chat_id)
            print("message_id→", message_id)
            print("update کامل:")
            print(update)
            print("=" * 50)
            text = str(update.get("message").get("content").get("text").get("text"))
            client.send_message(
                chat_id=chat_id,
                text="شلام تو گفتی "+text,
                reply_to=message_id
            )
            client.pin_message(chat_id, message_id)

        # این خط مهم است
        client.listen_for_updates(
            handler=on_new_message,
            self_messages=False,
            poll_interval=0.35
        )

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
