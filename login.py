import json
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


SESSION_FILE = "my.session"


def save_local_storage(driver):
    storage = driver.execute_script("""
        const data = {};

        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            data[key] = localStorage.getItem(key);
        }

        return data;
    """)

    storage["pwas"] = "1"

    with open(
        SESSION_FILE,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            storage,
            f,
            ensure_ascii=False,
            indent=2
        )


def get_phone():
    while True:
        phone = input("Phone number (98): ").strip()

        if not phone.startswith("98"):
            print("Error: Phone number must start with 98.")
            continue

        if not phone.isdigit():
            print("Error: Phone number must contain only numbers.")
            continue

        if len(phone) < 10:
            print("Error: Phone number is too short.")
            continue

        confirm = input(
            f"Is this number correct? {phone} (Y/N): "
        ).strip().lower()

        if confirm == "y":
            return phone

        if confirm == "n":
            continue


def submit_phone(driver, wait):
    button = wait.until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                "button[type='submit']"
                ".Button.default.primary.has-ripple"
            )
        )
    )

    wait.until(
        lambda d:
        button.is_enabled()
        and button.get_attribute("disabled") is None
    )

    try:
        button.click()
    except Exception:
        driver.execute_script(
            "arguments[0].click();",
            button
        )


def enter_phone(driver, wait):
    phone = get_phone()

    field = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input[type='tel']")
        )
    )

    field.click()
    field.clear()

    for char in phone:
        field.send_keys(char)

    submit_phone(driver, wait)


def check_code_status(driver):
    try:
        if driver.find_elements(
            By.ID,
            "search-input"
        ):
            return "success"

        fields = driver.find_elements(
            By.ID,
            "sign-in-code"
        )

        if not fields:
            return "waiting"

        aria = (
            fields[0].get_attribute("aria-label")
            or ""
        )

        if aria == "کد نامعتبر است.":
            return "invalid"

        if "منقضی" in aria:
            return "expired"

        return "waiting"

    except Exception:
        return "waiting"


def wait_code_result(driver):
    for _ in range(60):
        status = check_code_status(driver)

        if status != "waiting":
            return status

        time.sleep(1)

    return "timeout"


def enter_code(driver, wait):
    while True:
        field = wait.until(
            EC.visibility_of_element_located(
                (By.ID, "sign-in-code")
            )
        )

        code = input("Login code: ").strip()

        if not code:
            continue

        field.click()
        field.clear()
        field.send_keys(code)

        # کد توسط خود سایت submit می‌شود
        result = wait_code_result(driver)

        if result == "success":
            save_local_storage(driver)
            print("Login successful.")
            return True

        if result == "invalid":
            print("Invalid code. Try again.")
            continue

        if result == "expired":
            print("Code expired.")
            return False

        if result == "timeout":
            print("No result after 60 seconds.")
            return False


def login(driver):
    wait = WebDriverWait(driver, 30)

    while True:
        enter_phone(driver, wait)

        if enter_code(driver, wait):
            return True