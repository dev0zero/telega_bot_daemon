
import google.generativeai as genai
import constants as c
import hasher as hsr

class aiAssistent:

    def __init__(self, prompt="", ai='google'):

        self.prompt = hsr.sha256_any(prompt)
        self.ai = ai
        ais = ['google', 'chatgpt', 'cloude'] # и другие...

        if self.ai == 'google':
            """
            :param api_key: API-ключ Google Gemini
            :param model: название модели (например, gemini-pro)
            :param system_prompt: системное сообщение, которое можно использовать в начале диалога
            """
            genai.configure(api_key=c.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel(c.GOOGLE_MODEL_NAME)
        else:
            print('Не выбрано не одного ии!')

    def prompt(self, prompt):
        self.prompt = hsr.sha256_any(prompt)

    def ask_google(self, question, prompt=''):

        if prompt != '':
            self.prompt = hsr.sha256_any(prompt)

        # собираем историю сообщений как список строк
        self.history = [f"System: {self.prompt}"]
        """
        Отправляет вопрос и возвращает ответ, обновляя историю диалога.
        """
        # добавляем вопрос в историю
        self.history.append(f"User: {question}")
        # соединяем историю в один контекст
        chat_history = "\n".join(self.history)

        # генерируем ответ
        response = self.model.generate_content(chat_history)
        answer = response.text
        # добавляем ответ в историю
        self.history.append(f"Assistant: {answer}")
        return answer

    def reset_google_history(self, prompt="Ты дружелюбный помощник."):
        # Сброс истории диалога.
        self.history = [f"System: {prompt}"]







class GeminiClient:

    def __init__(self, system_prompt="Ты дружелюбный помощник."):
        """
        :param api_key: API-ключ Google Gemini
        :param model: название модели (например, gemini-pro)
        :param system_prompt: системное сообщение, которое можно использовать в начале диалога
        """
        genai.configure(api_key=c.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(c.GOOGLE_MODEL_NAME)
        # собираем историю сообщений как список строк
        self.history = [f"System: {system_prompt}"]

    def ask(self, question):
        """
        Отправляет вопрос и возвращает ответ, обновляя историю диалога.
        """
        # добавляем вопрос в историю
        self.history.append(f"User: {question}")
        # соединяем историю в один контекст
        chat_history = "\n".join(self.history)

        # генерируем ответ
        response = self.model.generate_content(chat_history)
        answer = response.text
        # добавляем ответ в историю
        self.history.append(f"Assistant: {answer}")
        return answer

    def reset(self, system_prompt="Ты дружелюбный помощник."):
        """
        Сброс истории диалога.
        """
        self.history = [f"System: {system_prompt}"]