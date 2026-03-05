# https://my.telegram.org/apps
import os
import asyncio

from traitlets import Bool

import constants as c
from datetime import datetime
# from askai import GeminiClient
from dateutils import DateUtils as dtm
from graph_creator import graph_creator
from telegram_model import TelegramModel
from dbutil import Mdb as Mysql
from telethon import TelegramClient, events
from debug import debug

class TelegramWatcher:
    def __init__(self):

        # подключение к телеграму
        self.client = TelegramClient(c.SESSION_NAME, c.API_ID, c.API_HASH)

        #self.allowed_chats =c.ALLOWED_CHAT_IDS
        # подключаемся к базе данных (MySQL)

        if not c.DISABLE_DB:
            self.db = Mysql()
            self.db.connect()
        else:
            self.db = None

        self.dtm = dtm()
        self.gc = graph_creator()
        # self.aichat = GeminiClient()
        self.model = TelegramModel()

        def users_as_proved_chats():

            # Добавляем всех кто пользователь, чтобы можно записывать текст с приватных сообщений
            r = self.db.get_all_saved_user_ids()
            print(r[0])
            for i in r:
                # TODO: установить привелегии каждому пользователю, он идет как чат
                # либо проверка пользователей не увидит и проигнорирует!!!
                # Посмотреть что с ID чата у пользователя
                break
                #pass

        # users_as_proved_chats()

    async def verify_access(self, event, command, params, bypass_command=False):

        res = await self.model.grant_access(event, bypass_command)
        if not res['access']:
            if res['message']:
                answer = f"{res['message']} -> {command}"
                reply = await event.reply(answer)
                if params['delete_msg']:
                    await asyncio.sleep(c.SLEEPTIMER['5sec'])
                    await self.client.delete_messages(event.chat_id, [event.id, reply.id])
            return False
        return res

    async def start(self):

        model = self.model

        @self.client.on(events.NewMessage())
        async def handler(event):

            res = await model.grant_access(event, bypass_command=True)

            if not res['access']:
                return

            dbg = debug()
            chat = await event.get_chat()
            sender = await event.get_sender()
            # sender_id = event.sender_id
            # chat_username = getattr(chat, 'username', None)

            if c.DEBUG:
                await dbg.ser(event)
                print('Skipped adding in to DB! Debugging enabled.')
                print("-------------------------------------------")
                print(sender.username)
                print(event.message.text)

                return

            if not c.SAVE_MESSAGES_TO_DB:
                print('Save messages in to DB disabled!')
            else:

                # тут работа с БД добавляем все, что можно в базу данных
                reply_user_id = 0
                reply_message_id = 0

                # проверка, есть ли ответ на чей то комментарий
                if event.message.is_reply:
                    # Получаем объект сообщения, на которое был ответ
                    replied_msg = await event.message.get_reply_message()
                    reply_message_id = event.message.reply_to_msg_id

                    if replied_msg and hasattr(replied_msg.from_id, "user_id"):
                        reply_user_id = replied_msg.from_id.user_id
                    else:
                        print("Не удалось получить сообщение, на которое был дан ответ.")

                self.db.insert_data("messages", {
                    "message_body": event.message.text,
                    "message_id": event.message.id,
                    "chat_id": event.message.chat_id,
                    "user_id": event.sender_id,
                    "reply_user_id": reply_user_id,
                    "reply_message_id": reply_message_id,
                    "message_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                })

                # Добавление/обновление пользователя
                self.db.add_or_update_user(
                    {
                        "telegram_id": sender.id,
                        "nickname": f"{sender.username}" if sender.username else "",
                        "firstname": sender.first_name or "",
                        "lastname": sender.last_name or "",
                        "email": f"{sender.email}" if sender.email else "",
                        "phone": f"{sender.phone}" if sender.phone else "",  # sender.phone,
                    }
                )

            # Сохранение файлов с чата

        # Выводит статус сервера, работает или нет
        @self.client.on(events.NewMessage(pattern=c.COMMANDSS['status_cmd']['command']))
        async def handler(event):

            delete_msg = False

            res = await self.verify_access(event, c.COMMANDSS['status_cmd']['command'], {"delete_msg": False})

            if not res:
                return False

            answer = f"{model.answer()}"

            reply = await event.respond(f"{answer}")

            if delete_msg:
                await asyncio.sleep(c.SLEEPTIMER['5sec'])
                await self.client.delete_messages(event.chat_id, [event.id, reply.id])

        @self.client.on(events.NewMessage(pattern=c.COMMANDSS['gpt_cmd']['command']))
        async def handler(event):

            res = await self.verify_access(event, c.COMMANDSS['gpt_cmd']['command'], {"delete_msg": False})

            if not res:
                return False

            answer = "Токен и API под ИИ еще не определенны!"
            reply = await event.reply(answer)


            '''
            delete_msg = False

            if not event.message.text:
                answer = f"Нужно что-то спросить! Пример: {c.COMMANDSS['gpt_cmd']['command']} [твой вопрос]!"
            else:
                answer = "ask ai a question!"

            # reply = await event.respond(answer)
            reply = await event.reply(answer)

            if delete_msg:
                await asyncio.sleep(c.SLEEPTIMER['5sec'])
                await self.client.delete_messages(event.chat_id, [event.id, reply.id])
            '''

        @self.client.on(events.NewMessage(pattern=c.COMMANDSS['help_cmd']['command']))
        async def handler(event):

            res = await self.verify_access(event, c.COMMANDSS['help_cmd']['command'], {"delete_msg": False})

            if not res:
                return False

            help_commands = self.model.list_commands(c.COMMANDSS, res['user_level'])

            # Удаляет сообщение на которое он отреагировал
            await self.client.delete_messages(event.chat_id, [event.id])
            await event.respond("Вот список команд...")
            await event.reply(f"{help_commands}")

        @self.client.on(events.NewMessage(pattern=c.COMMANDSS['list_chats_cmd']['command']))
        async def handler(event):

            res = await self.verify_access(event, c.COMMANDSS['list_chats_cmd']['command'], {"delete_msg": False})

            if not res:
                return False

            chats = await model.list_all_chats(self.client)
            for chunk in model.split_message(chats):
                await event.reply(chunk)

        @self.client.on(events.NewMessage(pattern=c.COMMANDSS['stats_cmd']['command']))
        async def handler(event):

            res = await self.verify_access(event, c.COMMANDSS['list_chats_cmd']['command'], {"delete_msg": False})
            if not res:
                return False

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
            stri += " чуть более сокрушенный вариант days:7/weeks:3/months:3/years:1 "
            stri += " или короткий вариант d1/w3/m1/y1 "

            try:
                lower_text = res['text_body'].lower().split()

                if len(lower_text) < 1:
                    raise Exception(stri)

                today_found = True

                for word in lower_text:
                    (from_date, to_date) = self.dtm.range(word)
                    if from_date is None or to_date is None:
                        raise Exception("некорректные даты")

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
                await event.reply(err_found)
            finally:
                pass

        @self.client.on(events.NewMessage(pattern="Какой_то_триггер_который_выводит_сообщение_00001"))
        async def handler(event):

            delete_msg = False
            sender = await event.get_sender()

            # ОПАСНО МОЖЕТ ВЫКИНУТЬ В ЛЮБОЙ ЧАТ В СПИСКЕ!!!
            r = await event.reply(f" 🛸 НЛО прилетело и оставило эту надпись! {sender.first_name}")

            if delete_msg:
                await asyncio.sleep(c.SLEEPTIMER['20sec'])
                await self.client.delete_messages(event.chat_id, [r.id, event.id])

        @self.client.on(events.NewMessage(pattern=c.COMMANDSS['report_cmd']['command']))
        async def handler():
            #await event.reply()
            #reply = await Model.search_user(event, self.db)
            pass

        @self.client.on(events.MessageEdited)
        async def handler(event):

            res = await model.grant_access(event, bypass_command=True)

            if not res['access']:
                return

            chat = await event.get_chat()
            sender = await event.get_sender()

            print("----- ОТРЕДАКТИРОВАНО -----")
            print("Чат:", getattr(chat, 'title', None) or chat.id)
            print("Пользователь:", getattr(sender, 'username', None) or sender.id)
            print("Текст:", event.raw_text)
            print("---------------------------")

            msg = event.message

            # если есть реакции
            if msg.reactions:
                for reaction in msg.reactions.results:
                    emoji = None

                    # обычный эмодзи
                    if hasattr(reaction.reaction, "emoticon"):
                        emoji = reaction.reaction.emoticon

                    # кастомный emoji (премиум)
                    elif hasattr(reaction.reaction, "document_id"):
                        emoji = f"custom_{reaction.reaction.document_id}"

                    print("Реакция:", emoji)
                    print("Количество:", reaction.count)
                    print("Я поставил?:", reaction.reaction)

        print("🚀 Бот запущен. Ожидаем сообщения...")

    def run(self):
        with self.client:
            self.client.loop.run_until_complete(self.start())
            self.client.run_until_disconnected()