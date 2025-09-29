import os
import asyncio
from datetime import datetime
from telethon import TelegramClient, events
import constants as c
import status as s
from dbutil import Mysqldatabase as Mysql
from askai import GeminiClient
from commentator import Commentator
from graph_creator import graph_creator
from dateutils import DateUtils as dtm
import re

# https://my.telegram.org/apps


class TelegramWatcher:
    def __init__(self):

        self.api_id = c.API_ID
        self.api_hash = c.API_HASH
        self.session_name = c.SESSION_NAME
        self.allowed_chats =c.ALLOWED_CHAT_IDS
        # подключаемся к базе данных (MySQL)
        self.db = Mysql()
        # подключение к телеграму
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)
        # подключение к базе данных
        self.db.connect()
        # команды с привелегиями
        self.commentator = Commentator(c.COMMANDS)

        self.ai_engine()

        self.dtm = dtm()
        self.gc = graph_creator()
        self.aichat = GeminiClient()

    def ai_engine(self):
         pass

    def __del__(self):
        self.db.close()

    async def list_all_chats(self):
        dialogs = await self.client.get_dialogs()
        all_chats = []
        for dialog in dialogs:
            entity = dialog.entity
            name = getattr(entity, 'title', getattr(entity, 'first_name', 'Нет названия'))
            username = getattr(entity, 'username', None)
            all_chats.append(f"→ {name} | ID: {entity.id} | Username: @{username}")
        if c.DEBUG:
            print("\n📋 Список всех чатов:")
            print(all_chats)

        return "\n".join(all_chats)

    # на ошибку Message too long
    MAX_LENGTH = 4096
    def split_message(self, text):
        return [text[i:i + self.MAX_LENGTH] for i in range(0, len(text), self.MAX_LENGTH)]

    async def start(self):
        async def verify(event):
            chat = await event.get_chat()
            #sender = await event.get_sender()
            sender_id = event.sender_id
            chat_username = getattr(chat, 'username', None)

            result = {}

            if chat.id in self.allowed_chats or chat_username in self.allowed_chats:
                are_you_root = self.allowed_chats[chat.id]
                if sender_id is not None and sender_id in c.ADMIN_USERS:
                    are_you_root = c.PRIV['lvl3']
                # Выдаем команду, если команде разрешено исполнение в этом чате
                key, question = self.commentator.find_first_command(event.message.text, are_you_root)

                result['access'] = are_you_root
                result['command'] = key
                result['message'] = question

                return result
            else:
                return None

        async def search_user(event):
            text = event.raw_text

            found_user = None
            raw_user_data = None

            # Сначала ищем ID (id=число)
            id_match = re.search(r'id=(\d+)', text)
            if id_match:
                found_user = int(id_match.group(1))

            # Если ID не найден → ищем упоминание @username
            mention_match = re.search(r'@(\w+)', text)
            if mention_match:
                found_user = mention_match.group(1)

            try:
                if found_user is not None:
                    self.db.get_userdata_by_id(found_user)

            except Exception as e:
                await event.reply(f"Пользователь не найден. Ошибка {e}")

            return raw_user_data


        @self.client.on(events.NewMessage())
        async def handler(event):

            #if event.out:
            #    return  # Это мое сообщение — игнор

            chat = await event.get_chat()
            sender = await event.get_sender()
            sender_id = event.sender_id
            chat_username = getattr(chat, 'username', None)
            bypass_record = False  # не добавляет данных в БД

            if c.DEBUG:
                bypass_record = True

            # Пропуск автоответа
            if event.message.message == "✅ Принято!":
                return

            # Добавляем всех кто пользователь, чтобы можно записывать текст с приватных сообщений

            '''
            r = self.db.get_all_saved_user_ids()
            print(r[0])

            for i in r:
                # TODO: установить привелегии каждому пользователю, он идет как чат
                # либо проверка пользователей не увидит и проигнорирует!!!
                # Посмотреть что с ID чата у пользователя
                break
                #pass
            '''

            if chat.id in self.allowed_chats or chat_username in self.allowed_chats:
                result = await verify(event)
                # не записываем команды в базу данных
                if result['command'] is not None:
                    return

                if c.DEBUG:
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
                        print(f"[ГРУППА] {chat.title} [{chat.id}] > {sender.username or sender.first_name}: {event.message.message}")
                    else:
                        print(f"[Другое] данные не определенны!")

                    if sender is not None:
                        print(sender)

                # тут работа с БД добавляем все, что можно в базу данных
                reply_user_id = 0
                reply_message_id = 0

                # проверка, есть ли ответ на чей то комментарий
                if event.message.is_reply:
                    # Получаем объект сообщения, на которое был ответ
                    replied_msg = await event.message.get_reply_message()
                    reply_message_id = event.message.reply_to_msg_id

                    if c.DEBUG:
                        print(f"Пользователь ответил на сообщение с ID: {reply_message_id}")

                    if replied_msg and hasattr(replied_msg.from_id, "user_id"):
                        reply_user_id = replied_msg.from_id.user_id
                    else:
                        print("Не удалось получить сообщение, на которое был дан ответ.")

                sql_data = {
                    "telegram_id": sender.id,
                    "nickname": f"{sender.username}" if sender.username else "Нет username",
                    "firstname": sender.first_name or "",
                    "lastname": sender.last_name or "",
                    "email": "",
                    "phone": sender.phone,
                }
                # Добавление/обновление пользователя
                self.db.add_or_update_user(sql_data)

                if not bypass_record:
                    self.db.insert_data("messages", {
                        "message_body": event.message.text,
                        "message_id": event.message.id,
                        "chat_id": event.message.chat_id,
                        "user_id": event.sender_id,
                        "reply_user_id": reply_user_id,
                        "reply_message_id": reply_message_id,
                        "message_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    })

        # Выводит статус сервера, работает или нет
        @self.client.on(events.NewMessage(pattern=c.COMMANDS['status_cmd']['command']))
        async def handler(event):
            result = await verify(event)
            if result is None or result['command'] is None:
                reply = await event.reply(f"Нет доступа к команде {c.COMMANDS['status_cmd']['command']}")
                await asyncio.sleep(c.SLEEPTIMER['5sec'])
                await self.client.delete_messages(event.chat_id, [event.id, reply.id])
                return
            else:
                status = s.Status()
                # ответ на команду
                reply = await event.respond(f"{status.answer()}")
                # подождать пару секунд, чтобы пользователь успел увидеть
                await asyncio.sleep(c.SLEEPTIMER['5sec'])
                # удалить и команду, и ответ
                await self.client.delete_messages(event.chat_id, [event.id, reply.id])

        @self.client.on(events.NewMessage(pattern=c.COMMANDS['gpt_cmd']['command']))
        async def handler(event):
            result = await verify(event)
            if result is None:
                return
            elif result['command'] is None:
                reply = await event.reply(f"Нет доступа к команде {c.COMMANDS['gpt_cmd']['command']}")
                await asyncio.sleep(c.SLEEPTIMER['5sec'])
                await self.client.delete_messages(event.chat_id, [event.id, reply.id])
                return
            else:
                question = result['message']
                if question is not None:
                    answer = self.aichat.ask(question)
                else:
                    answer = "Нужно что-то спросить! Пример: /ask {твой вопрос}!"

                event.reply(answer)

        @self.client.on(events.NewMessage(pattern=c.COMMANDS['help_cmd']['command']))
        async def handler(event):
            result = await verify(event)
            if result is None:
                return
            elif result['command'] is None:
                reply = await event.reply(f"Нет доступа к команде {c.COMMANDS['help_cmd']['command']}")
                await asyncio.sleep(c.SLEEPTIMER['5sec'])
                await self.client.delete_messages(event.chat_id, [event.id, reply.id])
                return
            else:
                await self.client.delete_messages(event.chat_id, [event.id])
                # ответ на команду
                await event.respond("Вот список команд...")
                ans = self.commentator.listCommands(result['access'])
                await event.reply(ans)
                # подождать пару секунд, чтобы пользователь успел увидеть
                # await asyncio.sleep(c.SLEEPTIMER['30sec'])
                # удалить и команду, и ответ
                # await self.client.delete_messages(event.chat_id,[reply.id, ans_reply.id])  # reply.id - если удалить и ответ

        @self.client.on(events.NewMessage(pattern=c.COMMANDS['list_chats_cmd']['command']))
        async def handler(event):
            result = await verify(event)
            if result is None:
                return
            elif result['command'] is None:
                reply = await event.reply(f"Нет доступа к команде {c.COMMANDS['list_chats_cmd']['command']}")
                await asyncio.sleep(c.SLEEPTIMER['5sec'])
                await self.client.delete_messages(event.chat_id, [event.id, reply.id])
                return
            else:
                res = await self.list_all_chats()
                for chunk in self.split_message(res):
                    await event.reply(chunk)


        @self.client.on(events.NewMessage(pattern=c.COMMANDS['stats_cmd']['command']))
        async def handler(event):
            result = await verify(event)

            if result is None or result['command'] is None:
                reply = await event.reply(f"Нет доступа к команде {c.COMMANDS['stats_cmd']['command']} ")
                await asyncio.sleep(c.SLEEPTIMER['5sec'])
                await self.client.delete_messages(event.chat_id, [event.id, reply.id])
                return
            else:

                async def send_graph(event,title1):
                    if os.path.exists(graph_path):
                        await self.client.send_file(
                            entity=event.chat_id,  # может быть ID, username или peer
                            file=graph_path,  # путь к файлу
                            caption=title1
                        )
                        self.gc.remove_file()

                    else:
                        print("Не могу найти файл статистики!")

                self.dtm.set_format('%Y-%m-%d')

                graph_path = f"{c.WORKINGDIR}/graph_chart.png"

                self.gc.set_file_dir(graph_path)
                self.gc.set_chat_id(event.chat_id)

                stri = "Примеры вывода статистики по дням, неделям, месяцам и годам"
                stri += " today/yesterday/this_week/month/year "
                stri += " чуть более сокрашенно days:7/weeks:3/months:3/years:1 "
                stri += " или милималистично d1/w3/m1/y1 "

                err_found = False
                today_found = True
                stats_by_user = False




                try:
                    lower_text = result['message'].lower().split()

                    if len(lower_text) < 1:
                        raise Exception(stri)

                    for word in lower_text:
                        (from_date, to_date) = self.dtm.range(word)
                        if from_date is None or to_date is None:
                            raise Exception("некорректные даты")
                            break

                        result = self.db.fetch_all_comments(chat_id=event.chat_id, from_date=from_date, to_date=to_date)

                        # Генерация статистики
                        self.gc.set_data(result)
                        self.gc.get_comments_graph(from_date=from_date, to_date=to_date)

                        if from_date == to_date and today_found:
                            title = "Статистика за сегодняшний день {from_date}"
                            await send_graph(event, title)
                            self.gc.view_comments_by_hour()
                            title = f"По часовая статистика за {to_date}"
                            await send_graph(event, title)
                            today_found = False
                        else:
                            title = f"Статистика за период: {from_date} - {to_date}"
                            await send_graph(event, title)

                except Exception as e:
                    err_found = f"Ошибка в запросе! {e}"
                    print(e)
                finally:
                    pass

                if err_found:
                    reply = await event.reply(err_found)
                    #await asyncio.sleep(c.SLEEPTIMER['5sec'])
                    #await self.client.delete_messages(event.chat_id, [reply.id])

        @self.client.on(events.NewMessage(pattern="нло*"))
        async def handler(event):

            await search_user(event)

            # ОПАСНО МОЖЕТ ВЫКИНУТЬ В ЛЮБОЙ ЧАТ В СПИСКЕ!!!
            await event.reply(f"НЛО прилетело и оставило эту надпись! 🤫")
            await asyncio.sleep(c.SLEEPTIMER['20sec'])
            await self.client.delete_messages(event.chat_id, [event.id])


        @self.client.on(events.NewMessage(pattern=c.COMMANDS['status_serv_cmd']['command']))
        async def handler(event):
            result = await verify(event)
            if result is None:
                return
            elif result['command'] is None:
                reply = await event.reply(f"Нет доступа к команде {c.COMMANDS['status_serv_cmd']['command']} ")
                await asyncio.sleep(c.SLEEPTIMER['5sec'])
                await self.client.delete_messages(event.chat_id, [event.id, reply.id])
                return
            else:
                await event.reply("Данные статуса сервера, Не готово!")


        print("🚀 Бот запущен. Ожидаем сообщения...")
        '''
        @self.client.on(events.MessageEdited)
        async def handler(event):
            #event.chat_id = event.chat_id
            #event.message_id = event.message_id
            # Log the date of new edits
            print('Message', event.id, 'changed at', event.date)
        '''


    def run(self):
        with self.client:
            self.client.loop.run_until_complete(self.start())
            self.client.run_until_disconnected()