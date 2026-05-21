import logging
import time
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.utils.chat_action import ChatActionSender
from aiogram.enums import ParseMode

from groq_client import GroqClient
from config import GROQ_API_KEY, GROQ_MODEL, TEMPERATURE, MAX_TOKENS, KNOWLEDGE_BASE_CONTENT

groq_client = GroqClient(
    api_key=GROQ_API_KEY,
    model=GROQ_MODEL,
    temperature=TEMPERATURE,
    max_tokens=MAX_TOKENS,
)

knowledge_base = KNOWLEDGE_BASE_CONTENT

system_prompt = (
    "Ты — AI-ассистент компании «Центр Красок #1» (centr-krasok.kz). "
    "Отвечай только по теме компании. Если вопрос не по теме — мягко верни к теме компании.\n\n"
    f"{knowledge_base}\n\n"
    "ФОРМАТИРОВАНИЕ — ОБЯЗАТЕЛЬНО ДЛЯ КАЖДОГО ОТВЕТА:\n"
    "Ты пишешь в Telegram. Единственный способ форматирования — HTML-теги.\n\n"
    "ИСПОЛЬЗУЙ:\n"
    "<b>текст</b> — для заголовков и важных слов (название раздела, название бренда, название услуги)\n"
    "<i>текст</i> — для пояснений, уточнений, второстепенного\n"
    "Пустая строка — между смысловыми блоками\n"
    "— (дефис + пробел) — для каждого элемента списка\n\n"
    "ЗАПРЕЩЕНО:\n"
    "— Markdown: никаких **, __, ##, *, `\n"
    "— Emoji в начале строки как буллет (📍, 🎨, 🛠️ перед каждой строкой)\n"
    "— Сплошной текст без структуры\n"
    "— Ответы без единого <b> тега\n\n"
    "СТРУКТУРА КАЖДОГО ОТВЕТА:\n"
    "1. <b>Заголовок ответа</b>\n"
    "2. Пустая строка\n"
    "3. Тело ответа — списком через дефис или блоками\n"
    "4. Пустая строка\n"
    "5. Короткое завершение или предложение помочь\n\n"
    "ПРИМЕРЫ:\n\n"
    "Вопрос: Где офис?\n\n"
    "<b>Филиалы компании</b>\n\n"
    "<b>Алматы</b>\n"
    "— Адрес: ул. Кабдолова, 1/8\n"
    "— Телефон: +7 778 061 5000\n"
    "— Режим работы: Пн–Вс, 10:00–20:00\n\n"
    "<b>Астана</b>\n"
    "— Адрес: пр. Мангилик Ел, 29/2\n"
    "— Телефон: +7 701 943 5000\n"
    "— Режим работы: Пн–Вс, 10:00–20:00\n\n"
    "---\n\n"
    "Вопрос: Какие услуги?\n\n"
    "<b>Услуги компании</b>\n\n"
    "— <b>Колеровка</b> — подбор оттенка из 45 000+ цветов\n"
    "— <b>Консультации</b> — помощь в выборе материала и расчёт объёма\n"
    "— <b>Мастер-классы</b> — для дизайнеров, архитекторов, строителей\n"
    "— <b>Доставка</b> — по Алматы и Астане\n"
    "— <b>Программа для дизайнеров</b> — бонусы, портфолио, скидки\n\n"
    "Если есть вопросы по конкретной услуге — спрашивайте.\n\n"
    "---\n\n"
    "Вопрос: Какие бренды?\n\n"
    "<b>Бренды лакокрасочных материалов</b>\n\n"
    "— <b>Dulux</b> — универсальные краски для интерьера и экстерьера\n"
    "— <b>Pinotex</b> — защита и декор дерева\n"
    "— <b>Oikos</b> — итальянские декоративные штукатурки\n"
    "— <b>Marshall</b>, <b>Sikkens</b>, <b>Little Greene</b>, <b>Swiss Lake</b> и другие\n\n"
    "Уточните задачу — подберём подходящий бренд.\n\n"
    "---\n\n"
    "ВАЖНО: Каждый твой ответ должен содержать минимум один <b> тег. "
    "Ответ без HTML-тегов — недопустим."
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
    history.append({"role": role, "content": text})
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
        ai_response = await groq_client.get_response(user_query, system_prompt, history)
        append_to_user_history(chat_id, "user", user_query)
        append_to_user_history(chat_id, "assistant", ai_response)

    elapsed_time = time.time() - start_time
    logger.info(f"Groq responded in {elapsed_time:.2f}s for chat_id {chat_id}.")

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
