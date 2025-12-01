import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import (
    FSInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.enums import ChatAction
import logging

# Логи
logging.basicConfig(level=logging.INFO)

# Токен
BOT_TOKEN = "8324054424:AAFsS1eHNEom5XpTO3dM2U-NdFIaVkZERX0"
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Чат уведомлений
NOTIFY_CHAT_ID = -1003322951241

# ===================== ТЕКСТЫ =====================

TEXT_WELCOME = (
    "👋 **Привет! Это Артём и команда Foton Plus.**\n\n"
    "Выбери, что хочешь получить 👇"
)

TEXT_ABOUT = (
    "ℹ️ **О нас**\n\n"
    "Мы команда Foton Plus — специалисты по маркетингу и рекламе.\n"
    "Помогаем бизнесам запускать прибыльные кампании и масштабироваться.\n\n"
    "Хочешь узнать, что мы можем для тебя сделать? Жми кнопку «🚀 Тарифы»."
)

TEXT_TARIFFS = (
    "🚀 **Тарифы и услуги:**\n\n"
    "• Запуск рекламы под ключ — от 19 900 ₽\n"
    "• Настройка ретаргета — 7 000 ₽\n"
    "• Полное ведение — от 14 900 ₽/мес\n"
    "• Аудит рекламных кампаний — 3 900 ₽\n\n"
    "Написать менеджеру 👇\nhttps://t.me/bery_lydu"
)

VIDEO_URL = "https://youtu.be/P-3NZnicpbk"

# ===================== МЕНЮ =====================

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📘 Получить мануал")],
        [KeyboardButton(text="📊 KPI таблица")],
        [KeyboardButton(text="📑 Чек-лист")],
        [KeyboardButton(text="🎥 Смотреть видео")],
        [KeyboardButton(text="ℹ️ Узнать о нас")],
        [KeyboardButton(text="❓ Задать вопрос")],
        [KeyboardButton(text="🚀 Тарифы")],
    ],
    resize_keyboard=True
)

# ===================== ФУНКЦИЯ УВЕДОМЛЕНИЙ =====================

async def notify(action: str, user: types.User):
    username = f"@{user.username}" if user.username else user.full_name
    await bot.send_message(
        NOTIFY_CHAT_ID,
        f"🔔 {action}\n👤 {username} (ID: {user.id})"
    )

# ===================== START =====================

@dp.message(Command("start"))
async def start_cmd(message: types.Message):

    # имитация печати
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(0.5)

    await message.answer(TEXT_WELCOME, reply_markup=main_menu, parse_mode="Markdown")

    await notify("Запустил бота", message.from_user)

# ===================== МАНУАЛ =====================

@dp.message(F.text == "📘 Получить мануал")
async def send_manual(message: types.Message):

    await notify("Запросил мануал", message.from_user)

    path = "marketing_manual.pdf"

    if os.path.exists(path):
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        await asyncio.sleep(0.5)
        await message.answer_document(FSInputFile(path), caption="📘 Твой мануал")
    else:
        await message.answer("⚠️ Файл marketing_manual.pdf временно отсутствует.")

# ===================== KPI =====================

@dp.message(F.text == "📊 KPI таблица")
async def send_kpi(message: types.Message):

    await notify("Запросил KPI таблицу", message.from_user)

    path = "metrika.pdf"

    if os.path.exists(path):
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        await asyncio.sleep(0.5)
        await message.answer_document(FSInputFile(path), caption="📊 Таблица KPI")
    else:
        await message.answer("⚠️ Файл metrika.pdf не найден.")

# ===================== ЧЕК-ЛИСТ =====================

@dp.message(F.text == "📑 Чек-лист")
async def send_checklist(message: types.Message):

    await notify("Запросил чек-лист", message.from_user)

    path = "check_list.pdf"

    if os.path.exists(path):
        await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
        await asyncio.sleep(0.5)
        await message.answer_document(FSInputFile(path), caption="📑 Чек-лист")
    else:
        await message.answer("⚠️ Файл check_list.pdf не найден.")

# ===================== ВИДЕО =====================

@dp.message(F.text == "🎥 Смотреть видео")
async def send_video(message: types.Message):

    await notify("Смотрит видео", message.from_user)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Смотреть видео", url=VIDEO_URL)]
    ])

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(0.5)

    await message.answer(
        "🎥 **Видеоурок готов!**\n\nНажми кнопку ниже 👇",
        reply_markup=kb,
        parse_mode="Markdown"
    )

# ===================== О НАС =====================

@dp.message(F.text == "ℹ️ Узнать о нас")
async def about(message: types.Message):

    await notify("Открыл информацию о компании", message.from_user)

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(0.4)

    await message.answer(TEXT_ABOUT, parse_mode="Markdown")

# ===================== ВОПРОС =====================

@dp.message(F.text == "❓ Задать вопрос")
async def ask_question(message: types.Message):

    await notify("Хочет задать вопрос", message.from_user)

    await message.answer(
        "✉️ Напиши свой вопрос, и менеджер свяжется с тобой.\n\n"
        "Или сразу переходи в чат:\n👉 https://t.me/bery_lydu"
    )

# ===================== ТАРИФЫ =====================

@dp.message(F.text == "🚀 Тарифы")
async def tariffs(message: types.Message):

    await notify("Открыл тарифы", message.from_user)

    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)
    await asyncio.sleep(0.5)

    await message.answer(TEXT_TARIFFS, parse_mode="Markdown")

# ===================== СТАРТ БОТА =====================

async def main():
    logging.info("Бот запущен...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
