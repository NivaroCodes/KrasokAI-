import logging
import google.generativeai as genai
from typing import Optional
import config

logger = logging.getLogger("KrasokAI.GeminiClient")

SYSTEM_PROMPT = f"""Вы являетесь профессиональным AI-ассистентом компании «Центр Красок #1» (centr-krasok.kz).
Ваша главная цель — отвечать на вопросы пользователей вежливо, профессионально и лаконично.

ИНСТРУКЦИЯ ПО ОТВЕТАМ:
1. Отвечайте на вопросы ИСКЛЮЧИТЕЛЬНО на основе предоставленной ниже Базы Знаний компании centr-krasok.kz.
2. Если в Базе Знаний нет ответа на вопрос пользователя, вы должны четко и вежливо сообщить об этом. Например: «К сожалению, в имеющейся у меня информации нет деталей по этому вопросу. Рекомендуем обратиться к нам напрямую по телефону...» или аналогично.
3. Категорически запрещается выдумывать (галлюцинировать) факты, цены, адреса, бренды или условия, которых нет в Базе Знаний.
4. Если пользователь задает отвлеченный вопрос, не связанный с компанией «Центр Красок #1», ее товарами, услугами или ремонтом, вежливо верните его к теме компании. Например: «Я помогаю только по вопросам, связанным с компанией "Центр Красок #1", лакокрасочными материалами и ремонтом. Чем я могу помочь вам в рамках нашей продукции?»
5. Пишите грамотно на русском языке, разделяйте текст на смысловые абзацы для удобства чтения.
6. Always format your responses using HTML tags only for structured styling when needed. Use <b>bold</b> for headings, key metrics, addresses, and important brands. Use <i>italics</i> for secondary notes, quotes, or examples. Structure lists using emojis (like 🎨, 📍, 📞, 💬, ℹ️) and line breaks. Do not use markdown symbols (such as **, *, #, or asterisks/hashtags). Only use valid Telegram HTML tags (<b>, <i>, <u>, <code>, <a>) to avoid parsing errors.

==================================================
БАЗА ЗНАНИЙ COMPANY (centr-krasok.kz):
==================================================
{config.KNOWLEDGE_BASE_CONTENT}
==================================================
"""

class DualModelGeminiClient:
    def __init__(self, primary_key: str, primary_model: str, fallback_key: str, fallback_model: str, temperature: float, max_tokens: int):
        self.primary_key = primary_key
        self.primary_model = primary_model
        self.fallback_key = fallback_key
        self.fallback_model = fallback_model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.current_model = primary_model
        self.using_fallback = False
        self._init_primary()

    def _init_primary(self):
        genai.configure(api_key=self.primary_key)
        self.client = genai.GenerativeModel(self.primary_model)
        logger.info(f"Primary Gemini model initialized: {self.primary_model}")

    def _init_fallback(self):
        if not self.fallback_key:
            logger.warning("Fallback API key not configured")
            return False
        try:
            genai.configure(api_key=self.fallback_key)
            self.client = genai.GenerativeModel(self.fallback_model)
            self.current_model = self.fallback_model
            self.using_fallback = True
            logger.info(f"Fallback model activated: {self.fallback_model}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize fallback model: {e}")
            return False

    async def get_response(self, user_message: str, system_prompt: str, chat_history: list) -> str:
        try:
            return await self._query_model(user_message, system_prompt, chat_history)
        except Exception as e:
            error_str = str(e).lower()
            if any(trigger in error_str for trigger in ["429", "rate", "quota", "deadline"]):
                logger.warning(f"Rate limit detected on {self.current_model}: {e}")
                if not self.using_fallback and self._init_fallback():
                    try:
                        return await self._query_model(user_message, system_prompt, chat_history)
                    except Exception as fallback_error:
                        logger.error(f"Fallback model also failed: {fallback_error}")
                        return "Система временно недоступна. Пожалуйста, попробуйте через несколько секунд."
                else:
                    return "Система временно недоступна. Пожалуйста, попробуйте через несколько секунд."
            else:
                logger.error(f"Unexpected error: {e}")
                return "Произошла ошибка. Пожалуйста, попробуйте снова."

    async def _query_model(self, user_message: str, system_prompt: str, chat_history: list) -> str:
        messages = [{"role": "user", "content": system_prompt}]
        for msg in chat_history[-10:]:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content") or msg.get("parts") or ""})
        messages.append({"role": "user", "content": user_message})
        
        formatted_contents = []
        for msg in messages:
            formatted_contents.append({
                "role": msg["role"],
                "parts": [msg["content"]]
            })
            
        response = await self.client.generate_content_async(
            contents=formatted_contents,
            generation_config=genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            ),
        )
        return response.text
