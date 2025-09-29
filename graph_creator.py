import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import re
from datetime import datetime, date
import constants as c

# Класс для создания определенных графиков

class graph_creator:
    def __init__(self):
        pass

    data = None
    save_path = f"{c.WORKINGDIR}/graphics_chart.png"
    chat_id = None

    def set_file_dir (self, files_dir):
        self.save_path = files_dir

    def set_data(self, data):
        self.data = data

    def set_chat_id(self, chat_id):
        self.chat_id = chat_id

    def remove_file(self):
        if not os.remove(self.save_path):
            print("Файл не удалился!")

    # Показывает почасовые коментарии в течении дня (24 часа)
    def view_comments_by_hour(self):

        df = pd.DataFrame(self.data)
        df['message_date'] = pd.to_datetime(df['message_date'])
        # Добавляем колонку "час"
        df['hour'] = df['message_date'].dt.hour
        # Группируем: количество сообщений по каждому пользователю и часу
        grouped = df.groupby(['firstname', 'hour']).size().reset_index(name='message_count')

        # Строим график
        plt.figure(figsize=(12, 6))

        for user in grouped['firstname'].unique():
            user_data = grouped[grouped['firstname'] == user]
            plt.plot(user_data['hour'], user_data['message_count'], marker='o', label=f'User {user}')

        plt.title('Количество сообщений по часам (24 часа) для каждого пользователя')
        plt.xlabel('Час суток')
        plt.ylabel('Количество сообщений')
        plt.xticks(range(0, 24))  # Чтобы отобразить все часы от 0 до 23
        plt.legend(title="Username")
        plt.grid(True)
        plt.tight_layout()
        #plt.show()
        plt.savefig(self.save_path)
        plt.close()
        print(f"График сохранён как {self.save_path}")

    # Показывает статистику взаимодействий
    def relations_graph(self):

        df_chat = pd.DataFrame(self.data)
        df_chat = df_chat[df_chat['reply_user_id'].notna()]

        if df_chat.empty:
            return {"status": False, "text": f"❌ В чате {self.chat_id} нет взаимодействий."}
        else:
            # Матрица взаимодействий
            interaction_matrix = (
                df_chat.groupby([ 'firstname','reply_firstname'])
                .size()
                .unstack(fill_value=0)
            )
            # Сортируем по сумме сообщений
            row_order = interaction_matrix.sum(axis=1).sort_values(ascending=False).index
            col_order = interaction_matrix.sum(axis=0).sort_values(ascending=False).index
            interaction_matrix = interaction_matrix.loc[row_order, col_order]
            # Heatmap
            plt.figure(figsize=(10, 8))
            sns.heatmap(interaction_matrix, annot=True, fmt="d", cmap="Blues", cbar=True)
            plt.title(f"Матрица взаимодействий пользователей\nЧат {self.chat_id}")
            plt.xlabel("Кому ответили")
            plt.ylabel("Кто отвечал")
            plt.tight_layout()
            #plt.show()
            plt.savefig(self.save_path)
            plt.close()
            print(f"График сохранён как {self.save_path}")
            return {'status': True, 'text': ''}


    def get_comments_graph(self, from_date=None, to_date=None):

        def clean_emoji(text):
            # Удаляет все эмодзи и нестандартные символы
            return re.sub(r'[\U00010000-\U0010FFFF]', '', text)

        # Преобразуем даты
        if isinstance(from_date, str):
            from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
        if isinstance(to_date, str):
            to_date = datetime.strptime(to_date, '%Y-%m-%d').date()
        if not from_date:
            return {"status": False, "text": "Не указана дата."}

        if not to_date:
            to_date = from_date

        df = pd.DataFrame(self.data)

        if df.empty:
            return {"status": False, "text": "Нет данных для анализа."}

        df['message_date'] = pd.to_datetime(df['message_date'])
        df['date_only'] = df['message_date'].dt.date

        # Фильтрация по диапазону
        filtered = df[(df['date_only'] >= from_date) & (df['date_only'] <= to_date)]

        if self.chat_id is not None:
            filtered = filtered[filtered['chat_id'] == self.chat_id]
        if filtered.empty:
            return {"status": False, "text":f"Нет комментариев в диапазоне {from_date} — {to_date}"}

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
        plt.savefig(self.save_path)
        plt.close()
        print(f"График сохранён как {self.save_path}")
        return True