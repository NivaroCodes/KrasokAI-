import logging
from groq import AsyncGroq
import config

logger = logging.getLogger("KrasokAI.GroqClient")

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

class GroqClient:
    def __init__(self, api_key: str, model: str, temperature: float, max_tokens: int):
        self.client = AsyncGroq(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        logger.info(f"Groq client initialized: {self.model}")

    async def get_response(self, user_message: str, system_prompt: str, chat_history: list) -> str:
        try:
            messages = [{"role": "system", "content": system_prompt}]
            for msg in chat_history[-10:]:
                role = msg.get("role", "").strip()
                content = msg.get("content", "").strip()
                if not role or not content:
                    continue
                if role not in ("user", "assistant"):
                    role = "user"
                messages.append({
                    "role": role,
                    "content": content
                })
            messages.append({"role": "user", "content": user_message.strip()})
            logger.info(f"Sending {len(messages)} messages to Groq API")
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq API error: {e}")
            return "Произошла ошибка. Пожалуйста, попробуйте снова."
