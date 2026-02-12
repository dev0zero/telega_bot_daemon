import mysql.connector
from mysql.connector import Error
from datetime import datetime
import constants as c

class Mdb:
    def __init__(self):

        self.connection = None

    def connect(self):
        """Создание подключения к MySQL."""
        try:
            self.connection = mysql.connector.connect(
                host=c.HOST,
                database=c.DATABASE,
                user=c.USER,
                password=c.PASSWORD,
                charset=c.CHARSET,
            )
            if self.connection.is_connected():
                print("✅ Бот подключился к базе данных.")
        except Error as e:
            print(f"Ошибка подключения: {e}")

    def close(self):
        """Закрытие подключения."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Соединение с базой данных закрыто.")

    def insert_data(self, table, data):
        """
        Вставка данных в таблицу.
        :param table: Название таблицы.
        :param data: Словарь с ключами-столбцами и значениями.
        """
        if not self.connection or not self.connection.is_connected():
            raise ConnectionError("Сначала вызовите connect()")

        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        values = tuple(data.values())
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, values)
            self.connection.commit()
            if c.DEBUG:
                print(f"Данные успешно добавлены в таблицу {table}.")
        except Error as e:
            print(f"Ошибка при вставке данных: {e}")
        finally:
            self.close()

    # Тут получаем ID пользователя для дальнейшей работы с его данными в Базе Данных
    # к примеру поиск по nickname или firstname и получаем telegram ID

    def get_userdata_by_id(self, user_id=None):

        if not self.connection or not self.connection.is_connected():
            raise ConnectionError("Сначала вызовите connect()")
        # TODO:  search user by firstname or telegram id
        user_id = int(user_id)
        print(user_id)


    def get_all_saved_user_ids(self):

        if not self.connection or not self.connection.is_connected():
            raise ConnectionError("Сначала вызовите connect()")

        result = None
        try:
            cursor = self.connection.cursor()
            query = f"SELECT `telegram_id`,`nickname`  FROM `users`"
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows is not None:
                result = rows
            else:
                raise ConnectionError("Выташить пользователей смог")
        except Error as e:
            result = f'Ошибка получения: {e}'
            return result
        finally:
            self.close()

        return result

    def get_dates(self, chat_id=None, user_id=None):

        if chat_id is None:
            print("chat_id не указан в поиске да")
            return None
        elif not self.connection or not self.connection.is_connected():
            raise ConnectionError("Сначала вызовите connect()")

        dates = []
        params = [chat_id]

        query = "SELECT chat_id, MIN(message_date) AS first_date, MAX(message_date) AS last_date FROM messages WHERE chat_id = %s"

        if user_id is not None:
            query += " AND user_id = %s"
            params.append(user_id)
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            dates = cursor.fetchone()
            if len(dates) == 0:
                raise ConnectionError("даты пустые")
        except Error as e:
            print(e)
        finally:
            self.close()

        return dates

    def fetch_all_comments(self, chat_id=None, user_id=None, from_date=None, to_date=None):

        if not self.connection or not self.connection.is_connected():
            raise ConnectionError("Сначала вызовите connect()")

        # result = []
        params = []
        query = """
                SELECT 
                    m.uniq_id,
                    m.message_body,
                    m.user_id,
                    m.chat_id,
                    m.message_date,
                    m.reply_user_id,
                    m.reply_message_id,
                    u.nickname AS nickname,              -- автор сообщения
                    u.firstname,
                    u.telegram_id AS telegram_id,
                    u_reply.firstname AS reply_firstname   -- имя того, кому ответили
                FROM messages m
                LEFT JOIN users u ON m.user_id = u.telegram_id
                LEFT JOIN users u_reply 
                    ON m.reply_user_id = u_reply.telegram_id
                WHERE 1 = 1
                """

        if chat_id is not None:
            query += " AND m.chat_id = %s"
            params.append(chat_id)

        if user_id is not None:
            query += " AND m.user_id = %s"
            params.append(chat_id)

        if from_date is not None and to_date is not None:
            try:
                if isinstance(from_date, str):
                    from_date = datetime.strptime(from_date, "%Y-%m-%d")
                if isinstance(to_date, str):
                    to_date = datetime.strptime(to_date, "%Y-%m-%d")

                start_str = from_date.strftime("%Y-%m-%d 00:00:00")
                end_str = to_date.strftime("%Y-%m-%d 23:59:59")

                query += " AND m.message_date BETWEEN %s AND %s"
                params.append(start_str)
                params.append(end_str)
            except ValueError:
                print("Неверный формат from_date или to_date. Используйте 'YYYY-MM-DD'")
                return []

        query += " ORDER BY m.message_id DESC"

        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            return cursor.fetchall()
        except self.connection.Error as err:
            print(f"Ошибка: {err}")
            return []
        finally:
            self.close()

    def add_or_update_user(self, user):

        if not self.connection or not self.connection.is_connected():
            print("Сначала вызовите connect()")
            raise ConnectionError("Сначала вызовите connect()")

        try:
            cursor = self.connection.cursor(dictionary=True)
            query = """
                INSERT IGNORE INTO users (telegram_id, nickname, firstname, lastname, email, phone)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    nickname = VALUES(nickname),
                    firstname = VALUES(firstname),
                    lastname = VALUES(lastname),
                    email = VALUES(email)
            """
            cursor.execute(query,
                           (user['telegram_id'],
                            user['nickname'],
                            user['firstname'],
                            user['lastname'],
                            user['email'],
                            user['phone'])
                            )
            self.connection.commit()



        except self.connection.Error as err:
            print(f"Ошибка: {err}")
        finally:
            self.close()





