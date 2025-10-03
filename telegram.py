# https://my.telegram.org/apps
import os
import asyncio
import constants as c
from datetime import datetime
from askai import GeminiClient
from dateutils import DateUtils as dtm
from graph_creator import graph_creator
from telegram_model import TelegramModel
from dbutil import Mysqldatabase as Mysql
from telethon import TelegramClient, events
from debug import debug

class TelegramWatcher:
    def __init__(self):

        # подключение к телеграму
        self.api_id = c.API_ID
        self.api_hash = c.API_HASH
        self.session_name = c.SESSION_NAME
        self.client = TelegramClient(self.session_name, self.api_id, self.api_hash)

        #self.allowed_chats =c.ALLOWED_CHAT_IDS
        # подключаемся к базе данных (MySQL)
        self.db = Mysql()
        self.db.connect()

        self.dtm = dtm()
        self.gc = graph_creator()

        self.aichat = GeminiClient()

    async def start(self):

        Model = TelegramModel()

        @self.client.on(events.NewMessage())
        async def handler(event):

            bypass_record = c.DEBUG  # не добавляет данных в БД

            res = await Model.grant_access(event, bypass_command=True)

            dbg = debug()

            if res['access'] is False:
                print('no access')
                return False
            elif bypass_record:

                await dbg.ser(event)
                print('Skipping adding in to database data! Debugging enabled.')
                return False
            else:
                chat = await event.get_chat()
                sender = await event.get_sender()
                sender_id = event.sender_id
                chat_username = getattr(chat, 'username', None)

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
                # тут работа с БД добавляем все, что можно в базу данных
                reply_user_id = 0
                reply_message_id = 0

                # проверка, есть ли ответ на чей то комментарий
                if event.message.is_reply:
                    # Получаем объект сообщения, на которое был ответ
                    replied_msg = await event.message.get_reply_message()
                    reply_message_id = event.message.reply_to_msg_id

                    if c.DEBUG:
                        bypass_record = True
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

                self.db.insert_data("messages", {
                    "message_body": event.message.text,
                    "message_id": event.message.id,
                    "chat_id": event.message.chat_id,
                    "user_id": event.sender_id,
                    "reply_user_id": reply_user_id,
                    "reply_message_id": reply_message_id,
                    "message_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                })
                print('msg added')

        # Выводит статус сервера, работает или нет
        @self.client.on(events.NewMessage(pattern=c.COMMANDSS['status_cmd']['command']))
        async def handler(event):

            res = await Model.grant_access(event)
            delete_msg = False
            answer = False

            if res['access'] is False:
                if res['message']:
                    answer = f"{res['message']} -> {c.COMMANDSS['status_cmd']['command']}"
                    delete_msg = True
            else:
                # Получаем статус сервера и отправляем пользователю
                answer = f"{Model.answer()}"

            reply = await event.respond(f"{answer}")

            if delete_msg:
                await asyncio.sleep(c.SLEEPTIMER['5sec'])
                await self.client.delete_messages(event.chat_id, [event.id, reply.id])

        @self.client.on(events.NewMessage(pattern=c.COMMANDSS['gpt_cmd']['command']))
        async def handler(event):

            res = await Model.grant_access(event)

            delete_msg = False
            answer = False

            if res['access'] is False:
                if res['message']:
                    answer = f"{res['message']} -> {c.COMMANDSS['gpt_cmd']['command']}"
                    delete_msg = True
            else:
                if not res['text_body']:
                    answer = f"Нужно что-то спросить! Пример: {c.COMMANDSS['gpt_cmd']['command']} [твой вопрос]!"
                else:
                    answer = self.aichat.ask(res['text_body'])

            if answer:
                reply = await event.reply(answer)
                if  delete_msg:
                    await asyncio.sleep(c.SLEEPTIMER['5sec'])
                    await self.client.delete_messages(event.chat_id, [event.id, reply.id])

            print(res)

        @self.client.on(events.NewMessage(pattern=c.COMMANDSS['help_cmd']['command']))
        async def handler(event):

            res = await Model.grant_access(event)

            if res['access'] is False:
                if res['message']:
                    answer = f"{res['message']} -> {c.COMMANDSS['help_cmd']['command']}"
                    reply = await event.reply(answer)
                    await asyncio.sleep(c.SLEEPTIMER['5sec'])
                    await self.client.delete_messages(event.chat_id, [event.id, reply.id])
            else:
                help_commands = Model.list_сommands(c.COMMANDSS, res['user_level'])

                # Удаляет сообщение на которое он отреагировал
                await self.client.delete_messages(event.chat_id, [event.id])
                await event.respond("Вот список команд...")

                print(help_commands)

                await event.reply(f"{help_commands}")

        @self.client.on(events.NewMessage(pattern=c.COMMANDSS['list_chats_cmd']['command']))
        async def handler(event):

            res = await Model.grant_access(event)

            if res['access'] is False:
                if res['message']:
                    answer = f"{res['message']} -> {c.COMMANDSS['list_chats_cmd']['command']}"
                    reply = await event.reply(answer)
                    await asyncio.sleep(c.SLEEPTIMER['5sec'])
                    await self.client.delete_messages(event.chat_id, [event.id, reply.id])
            else:
                chats = await Model.list_all_chats(self.client)
                for chunk in Model.split_message(chats):
                    await event.reply(chunk)

        @self.client.on(events.NewMessage(pattern=c.COMMANDSS['stats_cmd']['command']))
        async def handler(event):

            res = await Model.grant_access(event)

            if res['access'] is False:
                if res['message']:
                    answer = f"{res['message']} -> {c.COMMANDSS['help_cmd']['command']}"
                    reply = await event.reply(answer)
                    await asyncio.sleep(c.SLEEPTIMER['5sec'])
                    await self.client.delete_messages(event.chat_id, [event.id, reply.id])
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
                    lower_text = res['text_body'].lower().split()

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
                            title = f"Статистика за сегодняшний день {from_date}"
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

        @self.client.on(events.NewMessage(pattern="н_л_о n1"))
        async def handler(event):

            delete_msg = False
            sender = await event.get_sender()

            # ОПАСНО МОЖЕТ ВЫКИНУТЬ В ЛЮБОЙ ЧАТ В СПИСКЕ!!!
            r = await event.reply(f" 🛸 НЛО прилетело и оставило эту надпись! {sender.first_name}")

            if delete_msg:
                await asyncio.sleep(c.SLEEPTIMER['20sec'])
                await self.client.delete_messages(event.chat_id, [r.id, event.id])

        @self.client.on(events.NewMessage(pattern=c.COMMANDSS['report_cmd']['command']))
        async def handler(event):

            #await event.reply()

            #reply = await Model.search_user(event, self.db)
            pass

        '''
        @self.client.on(events.MessageEdited)
        async def handler(event):
            #event.chat_id = event.chat_id
            #event.message_id = event.message_id
            # Log the date of new edits
            print('Message', event.id, 'changed at', event.date)
        '''

        print("🚀 Бот запущен. Ожидаем сообщения...")

    def run(self):
        with self.client:
            self.client.loop.run_until_complete(self.start())
            self.client.run_until_disconnected()