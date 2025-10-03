
class debug:
    def __init__(self):
        pass


    async def show_msg(self, event, msg):

        sender = event.get_sender()
        chat = await event.get_chat()
        sender_id = event.sender_id if sender else None
        print("======================================")
        # Ответ на другое сообщение
        if event.message.reply_to_msg_id:
            replied_msg = await event.get_reply_message()
            if replied_msg:
                print("↩️ Ответ на сообщение:")
                print(f">>> {replied_msg.text}")

        if not hasattr(sender, 'id'):
            print("sender has no id")
        if not hasattr(sender, 'username'):
            print("sender has no username")
        if not hasattr(sender, 'first_name'):
            print("sender has no first_name")
        if not hasattr(sender, 'last_name'):
            print("sender has no last_name")

        print(f"id сообщения -> {event.message.id}")
        print(f"Мой ID: {sender.id} {sender.username} {sender.first_name} {sender.last_name}")
        print(f"id чата -> {chat.id}")
        print(f"ID отправителя -> {sender_id}")
        print(f"id чата сообщения (message.chat_id) -> {event.message.chat_id}")

        # Канал
        if event.is_channel:
            print(f"[КАНАЛ] {chat.title} [{chat.id}]: {event.message.message}")
            # pass
        # Личное сообщение
        elif event.is_private:
            print(f"[ЛИЧНОЕ] {sender.username or sender.first_name} [{chat.id}]: {event.message.message}")
            # await event.reply("✅ Принято!")
        # Группа
        elif event.is_group:
            print(
                f"[ГРУППА] {chat.title} [{chat.id}] > {sender.username or sender.first_name}: {event.message.message}")
        else:
            print(f"[Другое] данные не определенны!")

        if sender is not None:
            print(sender)

    async def ser(self, event):
        sender = await event.get_sender()

        print(sender)
        print(f"Имя пользователя {sender.first_name} {sender.last_name}")