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
                text="شلام تو گفتی " + text,
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
