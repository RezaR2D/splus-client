
import subprocess
import sys
import importlib.util

"""
- برای نصب پیش نیاز ها ابتدا این فایل اجرا شود
- splus.ir 
- نوشته شده توسط https://github.com/RezaR2D
- تاریخ : 1405/05/31
- مناسب برای طراحی رباتهای سروش پلاس
"""
def is_installed(package_name):
    return importlib.util.find_spec(package_name) is not None


def get_version(package_name):
    try:
        mod = __import__(package_name)
        return getattr(mod, "__version__", "نامشخص")
    except Exception:
        return None


def install_packages(packages):
    """نصب پکیج‌ها با نمایش مستقیم خروجی pip"""

    print("\nدر حال نصب پکیج‌ها...\n")

    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--upgrade"
    ] + packages

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    for line in process.stdout:
        print(line, end="")

    process.wait()

    return process.returncode == 0


def main():

    print("=" * 50)
    print("Setup - بررسی و نصب پیش‌نیازها")
    print("=" * 50)

    # نام پکیج pip -> نامی که با import استفاده می‌شود
    packages = {
        "selenium": "selenium",
        "requests": "requests"
    }

    need_install = []

    print("\nبررسی وضعیت پکیج‌ها:\n")

    for package_name, import_name in packages.items():

        if is_installed(import_name):

            version = get_version(import_name)

            print(
                f"✅ {package_name:<10} "
                f"نصب است | نسخه: {version}"
            )

        else:

            print(
                f"❌ {package_name:<10} "
                f"نصب نیست"
            )

            need_install.append(package_name)

    # =========================================================
    # نصب پکیج‌های موردنیاز
    # =========================================================

    if need_install:

        print("\nپکیج‌های موردنیاز برای نصب:")

        for package in need_install:
            print(f"  • {package}")

        success = install_packages(
            need_install
        )

        if not success:

            print(
                "\n⚠️ خطا در نصب پکیج‌ها."
            )

            sys.exit(1)

    else:

        print(
            "\nهمه پکیج‌ها از قبل نصب بودند."
        )

    # =========================================================
    # بررسی نهایی
    # =========================================================

    print("\n" + "=" * 50)
    print("نتیجه نهایی:")
    print("=" * 50)

    all_ok = True

    for package_name, import_name in packages.items():

        ok = is_installed(import_name)

        if ok:
            status = "✅ OK"
        else:
            status = "❌ نیست"
            all_ok = False

        print(
            f"{package_name:<10}: {status}"
        )

    # =========================================================
    # نتیجه
    # =========================================================

    if all_ok:

        print(
            "\n🎉 همه پیش‌نیازها آماده‌اند!"
        )

        print(
            "🚀 می‌توانید main.py را اجرا کنید."
        )

    else:

        print(
            "\n⚠️ بعضی پکیج‌ها نصب نشدند."
        )

        sys.exit(1)

    print("=" * 50)


if __name__ == "__main__":
    main()