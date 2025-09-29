import mysql.connector
import pandas as pd
from datetime import datetime, date
import constants as c
import matplotlib.pyplot as plt
from sys import platform
import re

class CommentStatsAnalyzer:

    def __init__ (self):
        pass

    all_comments = None
    chat_id = None
    files_dir = None

    def set_files_dir (self, files_dir):
        self.files_dir = files_dir

    def set_chat_id(self, chat_id):
        self.chat_id = chat_id

    def set_comments(self, comments):
        self.all_comments = comments

    def filter_by_date_or_range(self, from_date=None, to_date=None, chat_id=None, save_path=f"{c.WORKINGDIR}/comments_chart.png", graphics=[]):
        """
        Возвращает статистику по конкретной дате или диапазону дат:
        username, comment_count, date.
        :param from_date: начальная дата (строка 'YYYY-MM-DD' или datetime.date)
        :param to_date: конечная дата (если не указана — фильтрация по одной дате)
        :param chat_id: необязательный фильтр по чату
        :param save_path: путь для сохранения графика
        :return: DataFrame с колонками: username, comment_count
        """
        def clean_emoji(text):
            # Удаляет все эмодзи и нестандартные символы
            return re.sub(r'[\U00010000-\U0010FFFF]', '', text)

        # Преобразуем даты
        if isinstance(from_date, str):
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
        if isinstance(to_date, str):
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
        if not from_date:
            print("Не указана дата.")
            return pd.DataFrame()
        if not to_date:
            to_date = from_date
        df = pd.DataFrame(self.all_comments)
        if df.empty:
            print("Нет данных для анализа.")
            return pd.DataFrame()
        df['message_date'] = pd.to_datetime(df['message_date'])
        df['date_only'] = df['message_date'].dt.date

        # Фильтрация по диапазону
        filtered = df[(df['date_only'] >= from_date) & (df['date_only'] <= to_date)]
        if chat_id is not None:
            filtered = filtered[filtered['chat_id'] == chat_id]
        if filtered.empty:
            print(f"Нет комментариев в диапазоне {from_date} — {to_date}")
            return pd.DataFrame()
        # Получаем username и очищаем от эмодзи
        filtered['username'] = filtered.apply(
            lambda row: clean_emoji(row['firstname']) if row['firstname'] else clean_emoji(
                row.get('nickname', 'unknown')),
            axis=1
        )

        # Группировка по username
        result = filtered.groupby('username').size().reset_index(name='comment_count')
        # Подпись диапазона
        date_label = from_date if from_date == to_date else f"{from_date} — {to_date}"
        # Построение графика
        plt.figure(figsize=(10, 6))
        plt.bar(result['username'], result['comment_count'], color='skyblue')
        plt.title(f'Активность по комментариям за {date_label}')
        plt.xlabel('Пользователи')
        plt.ylabel('Количество комментариев')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        #plt.show()
        plt.savefig(save_path)
        plt.close()
        print(f"График сохранён как {save_path}")
        return result

