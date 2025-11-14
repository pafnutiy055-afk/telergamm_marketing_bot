import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton

# --- Настройка токена ---
BOT_TOKEN = "8324054424:AAFsS1eHNEom5XpTO3dM2U-NdFIaVkZERX0"  # твой токен
dp = Dispatcher()
bot = Bot(token=BOT_TOKEN)

# --- Чат для уведомлений ---
NOTIFY_CHAT_ID = -1003322951241

# --- Текст приветствия ---
welcome_text = (
    "Привет! 👋\n"
    "Это Артем и команда Foton Plus.\n\n"
    "Мы рады приветствовать тебя в нашем образовательном пространстве по маркетингу! 🎯\n"
    "Здесь ты найдёшь всё, что нужно, чтобы быстро освоить маркетинг и применять его на практике:\n\n"
    "📘 Гайды и чек-листы – пошаговые инструкции по основам маркетинга и продаж.\n"
    "📄 Практические мануалы – конкретные кейсы и стратегии, которые реально работают.\n"
    "🎥 Видео-обучения – разборы инструментов и техник маркетинга, чтобы учиться быстрее.\n"
    "🖥 Вебинары – прямые трансляции с разбором кейсов, ответами на вопросы и живой практикой.\n"
    "💡 Советы и лайфхаки – короткие полезные рекомендации, которые экономят время и деньги.\n\n"
    "🎁 Первый подарок: бесплатный мини-гайд и обучающее видео по маркетингу, которые мы подготовили специально для тебя.\n"
    "⚡️ Совет от команды Foton Plus: изучай материалы, применяй их на практике и возвращайся к гайду снова — так результат будет быстрее."
)

def format_for_telegram_markdown(text: str) -> str:
    """Форматирование текста под Markdown."""
    lines = text.splitlines()

    bold_full_lines = {
        "Привет! 👋",
        "Это Артем и команда Foton Plus.",
        "Мы рады приветствовать тебя в нашем образовательном пространстве по маркетингу! 🎯"
    }
    for i, ln in enumerate(lines):
        if ln.strip() in bold_full_lines:
            lines[i] = f"*{ln.strip()}*"

    bullet_prefixes = ("📘", "📄", "🎥", "🖥", "💡")
    for i, ln in enumerate(lines):
        stripped = ln.lstrip()
        if stripped and stripped[0] in bullet_prefixes and " – " in ln:
            left, right = ln.split(" – ", 1)
            lines[i] = f"*{left}* – {right}"

    for i, ln in enumerate(lines):
        stripped = ln.lstrip()
        if stripped.startswith("🎁"):
            if ": " in ln:
                left, right = ln.split(": ", 1)
                lines[i] = f"*{left}:* {right}"
            else:
                lines[i] = f"*{ln.strip()}*"

    for i, ln in enumerate(lines):
        stripped = ln.lstrip()
        if stripped.startswith("⚡️"):
            lines[i] = f"> *{stripped}*"

    return "\n".join(lines)


# --- Обработчик /start ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    formatted = format_for_telegram_markdown(welcome_text)
    await message.answer(formatted, parse_mode="Markdown")

    # Кнопка "📘 Отправить мануал"
    manual_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📘 Получить мануал", callback_data="send_manual")]
    ])
    await message.answer("Готов получить свой первый подарок? 👇", reply_markup=manual_button)

    # --- Отправка уведомления в чат ---
    username_display = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
    await bot.send_message(NOTIFY_CHAT_ID, f"✅ Пользователь стартанул бота: {username_display} (ID: {message.from_user.id})")


# --- Обработка кнопки "Отправить мануал" ---
@dp.callback_query(F.data == "send_manual")
async def send_manual(callback: types.CallbackQuery):
    guide_path = "marketing_manual.pdf"

    if os.path.exists(guide_path):
        document = FSInputFile(guide_path)
        await callback.message.answer_document(document=document, caption="Вот твой мини-гайд 📖")
    else:
        await callback.message.answer("❌ К сожалению, файл гайда не найден.")

    # После отправки мануала — кнопка на видео
    video_button = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎥 Получить видео", callback_data="send_video")]
    ])
    await callback.message.answer("Хочешь посмотреть обучающее видео? 👇", reply_markup=video_button)


# --- Обработка кнопки "Отправить видео" ---
@dp.callback_query(F.data == "send_video")
async def send_video(callback: types.CallbackQuery):
    VIDEO_URL = "https://youtu.be/P-3NZnicpbk"
    video_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎥 Смотреть урок — Запуск рекламной кампании в Яндекс Директ",
            url=VIDEO_URL
        )]
    ])
    await callback.message.answer(
        "Также мы подготовили обучающее видео, как запустить свою первую рекламную кампанию. Смотри его прямо сейчас 👇",
        reply_markup=video_kb
    )

    # --- Отправка уведомления в чат ---
    username_display = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.full_name
    await bot.send_message(NOTIFY_CHAT_ID, f"🎬 Пользователь посмотрел видео: {username_display} (ID: {callback.from_user.id})")


# --- Запуск бота ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
