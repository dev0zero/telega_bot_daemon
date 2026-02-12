import os
from abc import ABC, abstractmethod
from dotenv import load_dotenv
import requests

# pip install dotenv requests

import openai
import google.generativeai as genai

load_dotenv()

# =========================================================
# 🔹 БАЗОВЫЙ КЛАСС ПРОВАЙДЕРА
# =========================================================
class BaseAIProvider(ABC):
    @abstractmethod
    def chat(self, prompt: str, model: str) -> str:
        pass


# =========================================================
# 🔹 OPENAI
# =========================================================
class OpenAIProvider(BaseAIProvider):
    def __init__(self):
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def chat(self, prompt: str, model: str) -> str:
        resp = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message["content"]


# =========================================================
# 🔹 GEMINI (Google)
# =========================================================
class GeminiProvider(BaseAIProvider):
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    def chat(self, prompt: str, model: str) -> str:
        m = genai.GenerativeModel(model)
        resp = m.generate_content(prompt)
        return resp.text


# =========================================================
# 🔹 GROK (xAI)
# =========================================================
class GrokProvider(BaseAIProvider):
    def __init__(self):
        self.api_key = os.getenv("GROK_API_KEY")
        self.url = "https://api.x.ai/v1/chat/completions"

    def chat(self, prompt: str, model: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}]
        }

        r = requests.post(self.url, headers=headers, json=data)
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


# =========================================================
# 🚀 ГЛАВНЫЙ РОУТЕР
# =========================================================
class ChatRouter:

    def __init__(self):
        self.providers = {
            "openai": OpenAIProvider(),
            "gemini": GeminiProvider(),
            "grok": GrokProvider()
        }

    def _detect_provider(self, model: str) -> str:
        model = model.lower()

        if model.startswith("gpt"):
            return "openai"
        if model.startswith("gemini"):
            return "gemini"
        if model.startswith("grok"):
            return "grok"

        raise ValueError(f"Unknown model: {model}")

    def chat(self, prompt: str, model: str) -> str:
        provider_name = self._detect_provider(model)
        provider = self.providers[provider_name]
        return provider.chat(prompt, model)

if __name__ == "__main__":
    #from ai_router import ChatRouter
    router = ChatRouter()
    print(router.chat("Объясни что такое API", "gpt-4.1"))
    print(router.chat("Объясни что такое API", "gemini-1.5-pro"))
    print(router.chat("Объясни что такое API", "grok-2-latest"))