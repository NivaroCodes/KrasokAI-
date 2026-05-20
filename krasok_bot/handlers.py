import logging
import time
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.chat_action import ChatActionSender
from aiogram.enums import ParseMode

from gemini_client import DualModelGeminiClient, SYSTEM_PROMPT
from config import PRIMARY_API_KEY, PRIMARY_MODEL, FALLBACK_API_KEY, FALLBACK_MODEL, TEMPERATURE, MAX_TOKENS

gemini_client = DualModelGeminiClient(
    primary_key=PRIMARY_API_KEY,
    primary_model=PRIMARY_MODEL,
    fallback_key=FALLBACK_API_KEY,
    fallback_model=FALLBACK_MODEL,
    temperature=TEMPERATURE,
    max_tokens=MAX_TOKENS,
)

logger = logging.getLogger("KrasokAI.Handlers")

router = Router()
conversation_history = {}
MAX_HISTORY_LEN = 10


def get_user_history(chat_id: int) -> list:
    if chat_id not in conversation_history:
        conversation_history[chat_id] = []
    return conversation_history[chat_id]


def append_to_user_history(chat_id: int, role: str, text: str):
    history = get_user_history(chat_id)
    history.append({"role": role, "parts": text})
    if len(history) > MAX_HISTORY_LEN:
        conversation_history[chat_id] = history[-MAX_HISTORY_LEN:]


def clear_user_history(chat_id: int):
    if chat_id in conversation_history:
        conversation_history[chat_id] = []


def split_message(text: str, max_length: int = 4000) -> list[str]:
    if len(text) <= max_length:
        return [text]

    chunks = []
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break

        split_idx = text.rfind("\n", 0, max_length)
        if split_idx == -1 or split_idx < max_length * 0.7:
            split_idx = text.rfind(" ", 0, max_length)
        if split_idx == -1 or split_idx < max_length * 0.7:
            split_idx = max_length

        chunks.append(text[:split_idx].strip())
        text = text[split_idx:].strip()

    return chunks


@router.message(Command("start"))
async def start_handler(message: Message):
    chat_id = message.chat.id
    clear_user_history(chat_id)
    welcome_text = (
        "👋 <b>Здравствуйте! Вас приветствует KrasokAI</b> — официальный AI-ассистент компании «Центр Красок #1» (centr-krasok.kz)!\n\n"
        "🎨 Я готов помочь вам с любыми вопросами по ассортименту лаков, красок, декоративных штукатурок, профессиональных малярных инструментов, а также по вопросам доставки, оплаты и расположения наших филиалов в Алматы и Астане.\n\n"
        "💬 <b>Просто напишите ваш вопрос прямо сюда</b>, и я с удовольствием отвечу вам!\n\n"
        "📍 <i>Вы можете очистить историю нашего общения в любой момент с помощью команды /clear.</i>"
    )
    await message.answer(welcome_text, parse_mode=ParseMode.HTML)


@router.message(Command("clear"))
async def clear_handler(message: Message):
    chat_id = message.chat.id
    clear_user_history(chat_id)
    await message.answer("🧹 <b>История диалога успешно очищена!</b> Можем начать общение с чистого листа.", parse_mode=ParseMode.HTML)


@router.message(Command("help"))
async def help_handler(message: Message):
    help_text = (
        "ℹ️ <b>Как пользоваться помощником KrasokAI:</b>\n\n"
        "1️⃣ <b>Задавайте любые вопросы о нашей продукции и услугах.</b> Например:\n"
        "   • <i>«Какие бренды красок у вас продаются?»</i>\n"
        "   • <i>«Где находится ваш магазин в Алматы?»</i>\n"
        "   • <i>«Какое время работы филиала в Астане?»</i>\n"
        "   • <i>«Какие у вас условия доставки и оплаты?»</i>\n"
        "   • <i>«Делаете ли вы колеровку красок?»</i>\n\n"
        "2️⃣ <b>Помните:</b> я умею отвечать только на вопросы, касающиеся нашей компании и ее товаров. На отвлеченные темы я вежливо откажусь отвечать.\n\n"
        "3️⃣ <b>Команды:</b>\n"
        "   • /start — перезапустить бота\n"
        "   • /clear — очистить контекст диалога\n"
        "   • /help — показать эту справку"
    )
    await message.answer(help_text, parse_mode=ParseMode.HTML)


@router.message(F.text)
async def text_message_handler(message: Message):
    chat_id = message.chat.id
    user_query = message.text.strip()
    if not user_query:
        return
    if len(user_query) > 1500:
        await message.answer("⚠️ Ваш вопрос слишком длинный. Пожалуйста, сократите его, чтобы я мог дать точный ответ.")
        return

    start_time = time.time()
    logger.info(f"Received message from user in chat_id {chat_id}: '{user_query[:50]}...'")

    async with ChatActionSender.typing(bot=message.bot, chat_id=chat_id):
        history = get_user_history(chat_id)
        ai_response = await gemini_client.get_response(user_query, SYSTEM_PROMPT, history)
        append_to_user_history(chat_id, "user", user_query)
        append_to_user_history(chat_id, "model", ai_response)

    elapsed_time = time.time() - start_time
    logger.info(f"Gemini responded in {elapsed_time:.2f}s for chat_id {chat_id}.")

    chunks = split_message(ai_response)
    for chunk in chunks:
        try:
            try:
                await message.answer(chunk, parse_mode=ParseMode.HTML)
            except Exception as html_err:
                logger.warning(f"HTML parsing failed, sending as plain text: {html_err}")
                await message.answer(chunk, parse_mode=None)
        except Exception as send_err:
            logger.error(f"Failed to send message chunk to chat_id {chat_id}: {send_err}")
