
import google.generativeai as genai
import constants as c

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