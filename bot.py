import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

BOT_TOKEN = "8324054424:AAFsS1eHNEom5XpTO3dM2U-NdFIaVkZERX0"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

NOTIFY_CHAT_ID = -1003322951241

welcome_text = (
    "Привет! 👋\n"
    "Это Артем и команда Foton Plus.\n\n"
    "Готов начать обучение по маркетингу? 🎯\n"
    "Последовательно выдаю материалы.\n"
)

user_state = {}

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer(welcome_text)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📘 Получить мануал", callback_data="get_manual")]
    ])
    await message.answer("Твой первый материал 👇", reply_markup=kb)

    username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
    await bot.send_message(NOTIFY_CHAT_ID, f"🔥 Новый старт: {username} (ID: {message.from_user.id})")

    user_state[message.from_user.id] = {"last_material": datetime.now()}

@dp.callback_query(F.data == "get_manual")
async def send_manual(callback: types.CallbackQuery):
    path = "marketing_manual.pdf"
    if os.path.exists(path):
        await callback.message.answer_document(FSInputFile(path), caption="📘 Мини-гайд по маркетингу")
    else:
        await callback.message.answer("❌ Файл marketing_manual.pdf не найден.")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Получить таблицу KPI", callback_data="get_kpi")]
    ])
    await callback.message.answer("Готов получить таблицу KPI? 👇", reply_markup=kb)

    user_state[callback.from_user.id]["last_material"] = datetime.now()

@dp.callback_query(F.data == "get_kpi")
async def send_kpi(callback: types.CallbackQuery):
    path = "kpi.pdf"
    if os.path.exists(path):
        await callback.message.answer_document(FSInputFile(path), caption="📊 Таблица KPI")
    else:
        await callback.message.answer("❌ Файл kpi.pdf не найден.")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📑 Получить чек-лист", callback_data="get_checklist")]
    ])
    await callback.message.answer("Дальше чек-лист 👇", reply_markup=kb)

    user_state[callback.from_user.id]["last_material"] = datetime.now()

@dp.callback_query(F.data == "get_checklist")
async def send_checklist(callback: types.CallbackQuery):
    path = "check_list.pdf"
    if os.path.exists(path):
        await callback.message.answer_document(FSInputFile(path), caption="📑 Чек-лист «Проверка кампании»")
    else:
        await callback.message.answer("❌ Файл check_list.pdf не найден.")

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎥 Получить видеоурок", callback_data="get_video")]
    ])
    await callback.message.answer("А теперь видео 👇", reply_markup=kb)

    user_state[callback.from_user.id]["last_material"] = datetime.now()

@dp.callback_query(F.data == "get_video")
async def send_video(callback: types.CallbackQuery):
    VIDEO_URL = "https://youtu.be/P-3NZnicpbk"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎥 Смотреть урок", url=VIDEO_URL)],
        [InlineKeyboardButton(text="🧠 Перейти к квизу", callback_data="start_quiz")]
    ])

    await callback.message.answer("Видео урок готов 👇", reply_markup=kb)

    username = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.full_name
    await bot.send_message(NOTIFY_CHAT_ID, f"🎬 Пользователь открыл видео: {username} (ID: {callback.from_user.id})")

    user_state[callback.from_user.id]["quiz_ready_at"] = datetime.now() + timedelta(hours=2)

@dp.callback_query(F.data == "start_quiz")
async def quiz_start(callback: types.CallbackQuery):
    await callback.message.answer("🧠 Вопрос 1: В какой нише вы работаете?")
    user_state[callback.from_user.id]["quiz_step"] = 1

@dp.message()
async def quiz_flow(message: types.Message):
    uid = message.from_user.id
    if uid not in user_state or "quiz_step" not in user_state[uid]:
        return

    step = user_state[uid]["quiz_step"]

    if step == 1:
        user_state[uid]["niche"] = message.text
        await message.answer("🧠 Вопрос 2: Какая цель вашей рекламы?")
        user_state[uid]["quiz_step"] = 2
    elif step == 2:
        user_state[uid]["goal"] = message.text
        await message.answer("🧠 Вопрос 3: Какой у вас опыт в рекламе?")
        user_state[uid]["quiz_step"] = 3
    elif step == 3:
        user_state[uid]["experience"] = message.text
        await message.answer("🧠 Вопрос 4: Где планируете запускаться?")
        user_state[uid]["quiz_step"] = 4
    elif step == 4:
        user_state[uid]["platform"] = message.text

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📩 Получить разбор", url="https://t.me/bery_lydu")]
        ])

        await message.answer(
            "🔥 Отлично! На основе твоих ответов мы можем подготовить персональный разбор твоей рекламной стратегии."
            "\nНажми на кнопку ниже и напиши менеджеру, чтобы получить бесплатный разбор 👇",
            reply_markup=kb
        )

        del user_state[uid]["quiz_step"]

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
