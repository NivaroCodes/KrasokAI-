import asyncio
import logging
import google.generativeai as genai
import google.api_core.exceptions
from typing import List, Dict, Any

import config

logger = logging.getLogger("KrasokAI.GeminiClient")

if config.GOOGLE_API_KEY:
    genai.configure(api_key=config.GOOGLE_API_KEY)
else:
    logger.critical("GOOGLE_API_KEY is not configured! Gemini API calls will fail.")

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

generation_config = genai.types.GenerationConfig(
    temperature=config.TEMPERATURE,
    max_output_tokens=config.MAX_TOKENS,
)

try:
    model = genai.GenerativeModel(
        model_name=config.GEMINI_MODEL,
        generation_config=generation_config,
        system_instruction=SYSTEM_PROMPT
    )
    logger.info(f"Gemini model initialized successfully with model name: {config.GEMINI_MODEL}")
except Exception as e:
    logger.error(f"Failed to initialize Gemini Model: {e}")
    try:
        model = genai.GenerativeModel(
            model_name=config.GEMINI_MODEL,
            generation_config=generation_config
        )
    except Exception as e2:
        logger.critical(f"All Gemini initialization attempts failed: {e2}")
        model = None


async def generate_response(user_message: str, chat_history: List[Dict[str, str]], retries: int = 3, initial_delay: float = 1.0) -> str:
    if not config.GOOGLE_API_KEY or "YOUR_GOOGLE_API_KEY" in config.GOOGLE_API_KEY:
        logger.error("Attempted Gemini call without a valid API Key.")
        return "⚠️ Извините, на сервере проводятся технические работы (не настроен API ключ). Пожалуйста, свяжитесь с нами напрямую по контактам на сайте centr-krasok.kz."

    if model is None:
        logger.critical("Gemini model is not initialized.")
        return "⚠️ Извините, произошла ошибка инициализации AI-модели на сервере. Обратитесь в техническую поддержку."

    contents = []
    for msg in chat_history:
        contents.append({
            "role": msg["role"],
            "parts": [msg["parts"]]
        })
    
    contents.append({
        "role": "user",
        "parts": [user_message]
    })

    delay = initial_delay
    for attempt in range(retries):
        try:
            logger.info(f"Sending request to Gemini API (Attempt {attempt + 1}/{retries})")
            response = await model.generate_content_async(contents)
            if response and response.text:
                return response.text
            else:
                logger.warning("Empty response from Gemini API.")
                return "К сожалению, мне не удалось сформулировать ответ. Попробуйте перефразировать вопрос."
        except google.api_core.exceptions.ResourceExhausted as e:
            logger.warning(f"Gemini API rate limit exceeded on attempt {attempt + 1}. Retrying in {delay}s... Error: {e}")
            if attempt == retries - 1:
                return "⚠️ Превышен лимит запросов к AI-серверу. Пожалуйста, попробуйте написать свой вопрос через несколько секунд."
            await asyncio.sleep(delay)
            delay *= 2
        except google.api_core.exceptions.InvalidArgument as e:
            logger.error(f"Invalid argument sent to Gemini API: {e}")
            return "⚠️ Техническая ошибка конфигурации AI. Пожалуйста, обратитесь к менеджеру компании."
        except Exception as e:
            logger.error(f"Unexpected error during Gemini API call: {e}")
            if attempt == retries - 1:
                return "⚠️ К сожалению, произошла техническая ошибка при обработке запроса. Пожалуйста, повторите вопрос позже."
            await asyncio.sleep(delay)
            delay *= 2

    return "⚠️ Не удалось получить ответ от AI-модели после нескольких попыток."
