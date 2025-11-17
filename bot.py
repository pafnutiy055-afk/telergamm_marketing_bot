import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton

# --- Настройка токена ---
BOT_TOKEN = "8324054424:AAFsS1eHNEom5XpTO3dM2U-NdFIaVkZERX0"
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
    "🎁 Первый подарок: мини-гайд, чек-лист перед запуском кампании, таблица KPI и видео.\n"
    "⚡️ Совет: изучай материалы и применяй — так результат будет быстрее."
)

def format_for_telegram_markdown(text: str) -> str:
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


# === /start ===
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    formatted = format_for_telegram_markdown(welcome_text)
    await message.answer(formatted, parse_mode="Markdown")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📘 Получить материалы", callback_data="get_materials")]
    ])
    await message.answer("Готов получить комплект материалов? 👇", reply_markup=kb)

    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
    await bot.send_message(NOTIFY_CHAT_ID, f"✅ Пользователь запустил бота: {username} (ID: {message.from_user.id})")


# === МЕНЮ материалов ===
@dp.callback_query(F.data == "get_materials")
async def menu_materials(callback: types.CallbackQuery):
    menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📕 Мини-мануал", callback_data="send_manual")],
        [InlineKeyboardButton(text="📑 Чек-лист перед запуском", callback_data="send_checklist")],
        [InlineKeyboardButton(text="📊 Таблица KPI", callback_data="send_kpi")],
        [InlineKeyboardButton(text="🎥 Видео-урок", callback_data="send_video")]
    ])

    await callback.message.answer("Выбери, что хочешь получить 👇", reply_markup=menu)


# === Мини-мануал ===
@dp.callback_query(F.data == "send_manual")
async def send_manual(callback: types.CallbackQuery):
    file_path = "marketing_manual.pdf"

    if os.path.exists(file_path):
        await callback.message.answer_document(
            FSInputFile(file_path),
            caption="📘 Твой мини-мануал по маркетингу"
        )
    else:
        await callback.message.answer("❌ Файл marketing_manual.pdf не найден.")

    username = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.full_name
    await bot.send_message(NOTIFY_CHAT_ID, f"📘 Пользователь скачал мини-мануал: {username} (ID: {callback.from_user.id})")


# === Чек-лист ===
@dp.callback_query(F.data == "send_checklist")
async def send_checklist(callback: types.CallbackQuery):
    file_path = "check_list.pdf"

    if os.path.exists(file_path):
        await callback.message.answer_document(
            FSInputFile(file_path),
            caption="📑 Чек-лист проверки рекламной кампании перед запуском"
        )
    else:
        await callback.message.answer("❌ Файл check_list.pdf не найден.")

    username = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.full_name
    await bot.send_message(NOTIFY_CHAT_ID, f"📑 Пользователь скачал чек-лист: {username} (ID: {callback.from_user.id})")


# === Таблица KPI ===
@dp.callback_query(F.data == "send_kpi")
async def send_kpi(callback: types.CallbackQuery):
    file_path = "metrika.pdf"

    if os.path.exists(file_path):
        await callback.message.answer_document(
            FSInputFile(file_path),
            caption="📊 Таблица KPI для анализа кампаний"
        )
    else:
        await callback.message.answer("❌ Файл metrika.xlsx не найден.")

    username = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.full_name
    await bot.send_message(NOTIFY_CHAT_ID, f"📊 Пользователь скачал таблицу KPI: {username} (ID: {callback.from_user.id})")


# === Видео ===
@dp.callback_query(F.data == "send_video")
async def send_video(callback: types.CallbackQuery):
    VIDEO_URL = "https://youtu.be/P-3NZnicpbk"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Смотреть видео", url=VIDEO_URL)]
    ])

    await callback.message.answer(
        "🎥 Видео-урок: запуск первой рекламной кампании в Яндекс Директ",
        reply_markup=kb
    )

    username = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.full_name
    await bot.send_message(NOTIFY_CHAT_ID, f"🎬 Пользователь посмотрел видео: {username} (ID: {callback.from_user.id})")


# === Start Bot ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
