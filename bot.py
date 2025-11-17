import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton

# --- Токен ---
BOT_TOKEN = "ТОКЕН_ТУТ"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- Чат для уведомлений ---
NOTIFY_CHAT_ID = -1003322951241

# --- Текст приветствия ---
welcome_text = (
    "Привет! 👋\n"
    "Это Артем и команда Foton Plus.\n\n"
    "Готов начать обучение по маркетингу? 🎯\n"
    "Последовательно выдаю материалы.\n"
)

def format_md(text: str) -> str:
    return "\n".join([f"*{line}*" if line.strip().endswith("🎯") else line for line in text.splitlines()])

# ================================
#           /START
# ================================
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    formatted = format_md(welcome_text)
    await message.answer(formatted, parse_mode="Markdown")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📘 Получить мануал", callback_data="get_manual")]
    ])
    await message.answer("Твой первый материал 👇", reply_markup=kb)

    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
    await bot.send_message(NOTIFY_CHAT_ID, f"🔥 Новый старт: {username} (ID: {message.from_user.id})")


# ================================
#      МАНУАЛ → KPI
# ================================
@dp.callback_query(F.data == "get_manual")
async def send_manual(callback: types.CallbackQuery):
    path = "marketing_manual.pdf"
    if os.path.exists(path):
        await callback.message.answer_document(
            FSInputFile(path),
            caption="📘 Мини-гайд по маркетингу"
        )
    else:
        await callback.message.answer("❌ Файл marketing_manual.pdf не найден.")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Получить таблицу KPI", callback_data="get_kpi")]
    ])
    await callback.message.answer("Готов получить таблицу KPI? 👇", reply_markup=kb)


# ================================
#       KPI → ЧЕК-ЛИСТ
# ================================
@dp.callback_query(F.data == "get_kpi")
async def send_kpi(callback: types.CallbackQuery):
    path = "kpi.pdf"
    if os.path.exists(path):
        await callback.message.answer_document(
            FSInputFile(path),
            caption="📊 Таблица KPI"
        )
    else:
        await callback.message.answer("❌ Файл kpi.pdf не найден.")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📑 Получить чек-лист", callback_data="get_checklist")]
    ])
    await callback.message.answer("Дальше чек-лист 👇", reply_markup=kb)


# ================================
#      ЧЕК-ЛИСТ → ВИДЕО
# ================================
@dp.callback_query(F.data == "get_checklist")
async def send_checklist(callback: types.CallbackQuery):
    path = "check_list.pdf"
    if os.path.exists(path):
        await callback.message.answer_document(
            FSInputFile(path),
            caption="📑 Чек-лист «Проверка кампании»"
        )
    else:
        await callback.message.answer("❌ Файл check_list.pdf не найден.")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎥 Получить видеоурок", callback_data="get_video")]
    ])
    await callback.message.answer("А теперь видео 👇", reply_markup=kb)


# ================================
#           ВИДЕО
# ================================
@dp.callback_query(F.data == "get_video")
async def send_video(callback: types.CallbackQuery):
    VIDEO_URL = "https://youtu.be/P-3NZnicpbk"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎥 Смотреть урок",
            url=VIDEO_URL
        )],
        [InlineKeyboardButton(
            text="🧠 Перейти к квизу",
            callback_data="start_quiz"
        )]
    ])

    await callback.message.answer(
        "Видео урок готов 👇",
        reply_markup=kb
    )

    username = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.full_name
    await bot.send_message(NOTIFY_CHAT_ID, f"🎬 Пользователь открыл видео: {username} (ID: {callback.from_user.id})")


# ================================
#           КВИЗ
# ================================
@dp.callback_query(F.data == "start_quiz")
async def quiz_start(callback: types.CallbackQuery):
    await callback.message.answer("🧠 Вопрос 1:\nЧто такое целевая аудитория?")

# ================================
#  Ключевое слово «жопа»
# ================================
@dp.message(F.text.lower() == "жопа")
async def skip_wait(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧠 Начать квиз", callback_data="start_quiz")]
    ])
    await message.answer("⏩ Пропуск включён!\nМожешь начать квиз прямо сейчас 👇", reply_markup=kb)


# ================================
#          START BOT
# ================================
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
