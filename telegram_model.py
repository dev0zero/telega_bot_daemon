
from dbutil import Mdb as Mysql
import constants as c
import re
import psutil

class TelegramModel:
    def __init__(self):
        pass

    # на ошибку Message too long
    MAX_LENGTH = 4096
    def split_message(self, text):
        return [text[i:i + self.MAX_LENGTH] for i in range(0, len(text), self.MAX_LENGTH)]

    async def grant_access(self, event, bypass_command=False):

        chat = await event.get_chat()
        sender_id = event.sender_id
        chat_username = getattr(chat, 'username', None)
        allowed_chats = c.ALLOWED_CHATS
        privileges_list = c.PRIVILEGES
        commands_list = c.COMMANDSS
        admin_list = c.ADMINS

        result = {
            "access": False,
            "message": [],
            "command": None,
            "text_body": None,
            'user_level': privileges_list['Guest'],
            'chat_level': privileges_list['Guest'],
            'command_levels': privileges_list['Guest'],
        }

        ids_chats = []
        names_chats = []

        for k, v in allowed_chats.items():
            ids_chats.append(v.get('chat_id'))
            names_chats.append(k)

        # проверяем есть ли вообще чат в списке
        if chat.id not in ids_chats:# or chat_username not in chat_names:
            if c.DEBUG:
                print("chat id is not in allowed list ids")
            return result
        else:
            # пропускаем проверку, если не нужно исполнять команду
            if bypass_command:
                result["access"] = True
                return result

        # получаем привелегии чата
        for key, value in allowed_chats.items():
            if value.get('chat_id') == chat.id:
                result["chat_level"] = value.get('level_id')
                break

        # Данная проверка нужна для чатов в которые не нужно вообще светить команды
        if sender_id is None:
            if c.DEBUG:
                print("user is not in admins list")
        else:
            for key, value in admin_list.items():
                if value.get('user_id') == sender_id:
                    result["user_level"] = value.get('level_id')
                    break

            command, text_body = self.find_first_command(event.message.text, commands_list)

            if text_body is not None:
                result["text_body"] = text_body

            for key_cmd, value in commands_list.items():
                if key_cmd == command:
                    result['command'] = command
                    result["command_levels"] = value.get('privileges')
                    break


        # Глушим все исполнения от всех пользователей и чатов с установкой Гость!
        if result["chat_level"] == privileges_list['Guest']:
            if c.DEBUG:
                print('User or Chat is unknown it is -> Guest quit')
            return result

        # TODO: посмотреть как это работает
        if result["chat_level"] > result["command_levels"]:
            result['message'].append("Данная команда в этом чате не может быть исполнена")
            return result

        if result["user_level"] == privileges_list['Guest']:
            result['message'].append("Нету доступа к команде")
            return result

        if result["user_level"] > result["command_levels"]:
            result['message'].append("Данный пользователь не может исполнить эту команду!")
            return result

        if result["command_levels"] == privileges_list['Guest']:
            result['message'].append("Данная команда администратором отключена!")
            return result

        result['access'] = True

        return result

    """
    Найти первую команду в тексте, которая доступна для данного уровня привилегий.
    Возвращает кортеж (ключ команды, оставшийся текст) или (None, None), если не найдено.
    """
    def find_first_command(self, text, commands):

        positions = []
        for key, data in commands.items():
            cmd = data['command']
            idx = text.find(cmd)
            if idx != -1:
                positions.append((idx, key, cmd))
        if not positions:
            return None, None  # ни одна доступная команда не найдена
        first_pos, first_key, first_cmd = min(positions, key=lambda x: x[0])
        rest = text[first_pos + len(first_cmd):].strip()
        return first_key, rest

    """
    Вернуть список команд, доступных для указанного уровня привилегий.
    """
    def list_commands(self, commands, user_privilege_level):

        # print(f"Список команд {commands}")
        # print(f"привелегии конкретного пользователя {user_privilege_level}")

        coms = []
        for key, data in commands.items():
            cmd = data['command']
            cmd_priv = data['privileges']
            if user_privilege_level <= cmd_priv:
                coms.append(f"→ {cmd}")

        return "\n".join(coms) if coms else "Нет доступных команд"

    # Выводит список всех чатов --> сохраненных в телеграме!!!
    async def list_all_chats(self, client):

        dialogs = await client.get_dialogs()
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

    async def search_user(self, event, db):
        result = {
            'err_message': "",
            'user_name': "",
        }
        text = event.raw_text
        found_user = None
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
                user = db.get_userdata_by_id(found_user)
                if user is None:
                    raise Exception('Нет данных по пользователю!')
                result['user_name'] = user
            else:
                raise Exception('Не определен пользователь')
        except Exception as e:
            err = f"Ошибка {e}"
            result['err_message'] = err
        finally:
            pass
        return result

    # Данные по серверу ---
    def answer(self):
        return f"Everything OK! \n {self.get_memory_usage()}"

    def get_cpu_usage(self):
        return psutil.cpu_percent(interval=1)

    def get_memory_usage(self):
        memory = psutil.virtual_memory()
        return {
            'Всего': f'{memory.total / (1024 ** 3):.2f} ГБ',
            'Используется': f'{memory.used / (1024 ** 3):.2f} ГБ',
            'Свободно': f'{memory.available / (1024 ** 3):.2f} ГБ',
            'Процент использования': f'{memory.percent}%'
        }