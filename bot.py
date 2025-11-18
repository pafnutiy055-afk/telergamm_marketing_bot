import os
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ChatAction # <-- Новый импорт для имитации печати
import logging # <-- Добавляем логирование для отладки

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# ВАЖНО: Смените токен в BotFather, так как старый был скомпрометирован
BOT_TOKEN = "8324054424:AAFsS1eHNEom5XpTO3dM2U-NdFIaVkZERX0" 

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

NOTIFY_CHAT_ID = -1003322951241

# Хранилище состояний
user_state = {}

# --- Тексты для высокой конверсии ---
TEXT_WELCOME = (
    "👋 **Привет! Это Артём и команда Foton Plus.**\n\n"
    "Мы не льем воду, мы даем инструменты, которые приносят деньги. 💸\n"
    "Я подготовил для тебя пошаговую систему по маркетингу.\n\n"
    "Готов забрать первый инструмент и усилить свой бизнес? 👇"
)

TEXT_MANUAL_SENT = (
    "📘 **Твой Мануал по маркетингу**\n\n"
    "Изучи его, чтобы понимать базу. Но теория без цифр — ничто.\n"
    "Готов взять под контроль показатели своего бизнеса?"
)

TEXT_KPI_SENT = (
    "📊 **Таблица KPI (Метрика)**\n\n"
    "Теперь ты видишь цифры. Но уверен ли ты, что твоя реклама настроена без ошибок?\n"
    "Держи чек-лист, который спас тысячи бюджетов от слива. 👇"
)

TEXT_CHECKLIST_SENT = (
    "📑 **Чек-лист «Проверка кампании»**\n\n"
    "Теперь ты защищен от глупых ошибок. \n"
    "🔥 А сейчас — самое главное. **Секретный видеоурок**, где я разбираю реальные стратегии."
)

TEXT_VIDEO_SENT = (
    "🎥 **ДОСТУП ОТКРЫТ!**\n\n"
    "В этом видео — концентрат опыта. Смотри внимательно, инсайты гарантированы.\n\n"
    "⏳ *Через 2 часа я вернусь с важным предложением.*"
)

TEXT_QUIZ_OFFER = (
    "🚀 **Прошло 2 часа! Как впечатления?**\n\n"
    "Материалы — это круто, но результат дает только **индивидуальная стратегия**.\n\n"
    "Давай я помогу адаптировать эти знания под ТВОЙ бизнес. \n"
    "Ответь на 4 простых вопроса, и мы составим план действий конкретно для тебя. 👇"
)

# --- Хендлеры ---

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    # Имитация печати
    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)
    await asyncio.sleep(0.5) 
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📘 Скачать мануал", callback_data="get_manual")]
    ])
    await message.answer(TEXT_WELCOME, reply_markup=kb, parse_mode="Markdown")

    try:
        username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
        await bot.send_message(NOTIFY_CHAT_ID, f"🔥 Новый лид: {username} (ID: {message.from_user.id})")
    except Exception as e:
        logging.error(f"Ошибка отправки уведомления о старте: {e}")

@dp.callback_query(F.data == "get_manual")
async def send_manual(callback: types.CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    
    # Имитация печати перед документом
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(0.5)

    path = "marketing_manual.pdf"
    if os.path.exists(path):
        await callback.message.answer_document(FSInputFile(path), caption="📘 Твой мануал")
    else:
        await callback.message.answer("⚠️ Файл marketing_manual.pdf временно недоступен, но мы работаем над этим.")

    # Имитация печати перед вторым сообщением
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(0.7)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Забрать таблицу KPI", callback_data="get_kpi")]
    ])
    await callback.message.answer(TEXT_MANUAL_SENT, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "get_kpi")
async def send_kpi(callback: types.CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id

    # Имитация печати перед документом
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(0.5)

    path = "metrika.pdf"
    if os.path.exists(path):
        await callback.message.answer_document(FSInputFile(path), caption="📊 Таблица KPI")
    else:
        await callback.message.answer("⚠️ Файл metrika.pdf не найден.")
    
    # Имитация печати перед вторым сообщением
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(0.7)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📑 Получить чек-лист", callback_data="get_checklist")]
    ])
    await callback.message.answer(TEXT_KPI_SENT, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "get_checklist")
async def send_checklist(callback: types.CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id

    # Имитация печати перед документом
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(0.5)
    
    path = "check_list.pdf"
    if os.path.exists(path):
        await callback.message.answer_document(FSInputFile(path), caption="📑 Чек-лист")
    else:
        await callback.message.answer("⚠️ Файл check_list.pdf не найден.")

    # Имитация печати перед вторым сообщением
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(0.8)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎥 Смотреть видеоурок", callback_data="get_video")]
    ])
    await callback.message.answer(TEXT_CHECKLIST_SENT, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "get_video")
async def send_video(callback: types.CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    VIDEO_URL = "https://youtu.be/P-3NZnicpbk"
    
    # Имитация печати
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(1.0) 

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ СМОТРЕТЬ УРОК", url=VIDEO_URL)]
    ])
    await callback.message.answer(TEXT_VIDEO_SENT, reply_markup=kb, parse_mode="Markdown")

    username = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.full_name
    await bot.send_message(NOTIFY_CHAT_ID, f"🎬 Лид смотрит видео: {username} (ID: {callback.from_user.id})")

    # ЗАПУСК ФОНОВОЙ ЗАДАЧИ: Таймер на 2 часа
    asyncio.create_task(delayed_quiz_offer(callback.message.chat.id))

async def delayed_quiz_offer(chat_id: int):
    """Функция ожидания и отправки приглашения на квиз (без имитации печати)"""
    # Этот таймер остается без имитации печати, чтобы не занимать ресурсы
    await asyncio.sleep(2 * 60 * 60) # Ждем 2 часа (7200 секунд)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧠 ПРОЙТИ РАЗБОР", callback_data="start_quiz")]
    ])
    
    try:
        await bot.send_message(chat_id, TEXT_QUIZ_OFFER, reply_markup=kb, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Не удалось отправить отложенное сообщение пользователю {chat_id}: {e}")

# --- Логика Квиза ---

@dp.callback_query(F.data == "start_quiz")
async def quiz_start(callback: types.CallbackQuery):
    await callback.answer()
    chat_id = callback.message.chat.id
    
    # Имитация печати
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(0.5)

    await callback.message.answer("1️⃣ **Вопрос 1:** В какой нише вы работаете?", parse_mode="Markdown")
    user_state[callback.from_user.id] = {"quiz_step": 1}
    
    username = f"@{callback.from_user.username}" if callback.from_user.username else callback.from_user.full_name
    await bot.send_message(NOTIFY_CHAT_ID, f"🧠 Лид начал квиз: {username}")

@dp.message(F.text)
async def quiz_flow(message: types.Message):
    uid = message.from_user.id
    chat_id = message.chat.id

    if uid not in user_state or "quiz_step" not in user_state[uid]:
        return

    step = user_state[uid]["quiz_step"]

    # Имитация печати перед каждым ответом бота
    await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    await asyncio.sleep(0.7) 

    if step == 1:
        user_state[uid]["niche"] = message.text
        await message.answer("2️⃣ **Вопрос 2:** Какая ГЛАВНАЯ цель вашей рекламы сейчас?", parse_mode="Markdown")
        user_state[uid]["quiz_step"] = 2
        
    elif step == 2:
        user_state[uid]["goal"] = message.text
        await message.answer("3️⃣ **Вопрос 3:** Какой у вас опыт в рекламе? (Новичок / Сливал бюджет / Профи)", parse_mode="Markdown")
        user_state[uid]["quiz_step"] = 3
        
    elif step == 3:
        user_state[uid]["experience"] = message.text
        await message.answer("4️⃣ **Вопрос 4:** На какой площадке планируете запускаться? (VK / Яндекс / Telegram / Другое)", parse_mode="Markdown")
        user_state[uid]["quiz_step"] = 4
        
    elif step == 4:
        user_state[uid]["platform"] = message.text

        # Сбор ответов для менеджера
        answers = (
            f"Ниша: {user_state[uid].get('niche')}\n"
            f"Цель: {user_state[uid].get('goal')}\n"
            f"Опыт: {user_state[uid].get('experience')}\n"
            f"Площадка: {user_state[uid].get('platform')}"
        )

        username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
        
        # Отправка заявки менеджеру
        await bot.send_message(
            NOTIFY_CHAT_ID, 
            f"✅ **КВИЗ ЗАВЕРШЕН!**\n👤: {username} (ID: {uid})\n\n📄 **Ответы:**\n{answers}"
        )

        # Имитация печати перед финальным сообщением
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
        await asyncio.sleep(1.0) 

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📩 ЗАБРАТЬ РАЗБОР", url="https://t.me/bery_lydu")]
        ])

        await message.answer(
            "🔥 **Спасибо! Я проанализировал твои ответы.**\n\n"
            "Мы подготовили стратегию специально под твою нишу.\n"
            "Нажми кнопку ниже, напиши менеджеру **«РАЗБОР»**, и мы бесплатно обсудим твой запуск! 👇",
            reply_markup=kb,
            parse_mode="Markdown"
        )

        # Очистка состояния
        if uid in user_state:
            del user_state[uid]

async def main():
    logging.info("Бот запущен...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
