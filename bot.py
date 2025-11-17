import os
import asyncio
from typing import Dict, Any, List
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage

# ----------------- Настройки -----------------
BOT_TOKEN = "8324054424:AAFsS1eHNEom5XpTO3dM2U-NdFIaVkZERX0"
NOTIFY_CHAT_ID = -1003322951241
VIDEO_URL = "https://youtu.be/P-3NZnicpbk"
MANUAL_FILE = "marketing_manual.pdf"
CHECKLIST_FILE = "check_list.pdf"
KPI_FILE = "metrika.pdf"
SELLER_USERNAME = "@E_L_0_A_X"
DELAY_SECONDS = 2 * 60 * 60  # 2 часа

# ----------------- Инициализация -----------------
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ----------------- Состояния пользователей -----------------
users_state: Dict[int, Dict[str, Any]] = {}

# ----------------- Клавиатуры -----------------
def kb_get_video():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("▶️ Смотреть урок и запустить рекламу", url=VIDEO_URL)]
    ])

def kb_start_quiz():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("🧠 Начать квиз", callback_data="start_quiz")]
    ])

# ----------------- Вопросы для квиза -----------------
QUIZ_QUESTIONS: List[Dict[str, Any]] = [
    {"text": "1) Какая у тебя ниша?", "opts": ["Услуги", "Товары", "Онлайн-школа", "Другое"]},
    {"text": "2) Какую цель ставишь для кампании?", "opts": ["Лиды", "Продажи", "Трафик", "Повышение узнаваемости"]},
    {"text": "3) Опыт в рекламе?", "opts": ["Запускаю впервые", "Настраивал пару раз", "Уверенно работаю", "Я профи"]},
    {"text": "4) Где планируешь запускаться?", "opts": ["Яндекс Директ", "VK / MyTarget", "Meta (Facebook/Instagram)", "Пока не знаю"]}
]

# ----------------- Утилиты -----------------
def ensure_user_state(user_id: int):
    if user_id not in users_state:
        users_state[user_id] = {
            "step": "started",
            "timer_task": None,
            "quiz": {"q_index": 0, "answers": []},
            "delayed_sent": False,
            "quiz_done": False
        }

def get_username_display(user: types.User) -> str:
    return f"@{user.username}" if user.username else user.full_name

# ----------------- Старт бота -----------------
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    ensure_user_state(user_id)

    greeting = (
        "Привет! 👋\nЭто Артем и команда Foton Plus.\n\n"
        "Добро пожаловать в образовательное пространство по маркетингу! 🎯\n"
        "🎁 Мы подготовили для тебя набор материалов, чтобы сразу применить их на практике.\n"
        "⚡️ Совет: изучай пошагово и запускай кампании уже сегодня!"
    )
    await message.answer(greeting)
    await bot.send_message(NOTIFY_CHAT_ID, f"✅ {get_username_display(message.from_user)} запустил бота (ID: {user_id})")

    # ----------------- Отправка материалов с задержкой -----------------
    if os.path.exists(MANUAL_FILE):
        await message.answer_document(FSInputFile(MANUAL_FILE), caption="📘 Мини-мануал — стартовый материал")
        await asyncio.sleep(10)

    if os.path.exists(CHECKLIST_FILE):
        await message.answer_document(FSInputFile(CHECKLIST_FILE), caption="📑 Чек-лист: проверка рекламной кампании")
        await asyncio.sleep(10)

    if os.path.exists(KPI_FILE):
        await message.answer_document(FSInputFile(KPI_FILE), caption="📊 Таблица KPI для анализа кампаний")
        await asyncio.sleep(10)

    # ----------------- Видео сразу после KPI -----------------
    await message.answer(
        "🎥 Отлично! Теперь пора применить знания на практике.\n"
        "Смотри видеоурок «Запуск первой рекламной кампании в Яндекс Директ» и научись быстро привлекать лидов и контролировать бюджет.",
        reply_markup=kb_get_video()
    )
    users_state[user_id]["step"] = "video_sent"

    # ----------------- Запуск отложенного сообщения через 2 часа -----------------
    if users_state[user_id]["timer_task"] is None:
        users_state[user_id]["timer_task"] = asyncio.create_task(schedule_delayed_message(user_id))

# ----------------- Таймер и отложенное сообщение -----------------
async def schedule_delayed_message(user_id: int, delay_seconds: int = DELAY_SECONDS):
    try:
        await asyncio.sleep(delay_seconds)
    except asyncio.CancelledError:
        return

    st = users_state.get(user_id)
    if not st or st.get("delayed_sent") or st.get("quiz_done"):
        return

    try:
        await bot.send_message(user_id,
                               "⏰ Ты уже посмотрел видео и материалы? Хочешь разбор твоей рекламной кампании?",
                               reply_markup=kb_start_quiz())
        st["delayed_sent"] = True
    except Exception:
        pass

# ----------------- Ключевое слово "жопа" -----------------
@dp.message()
async def skip_timer_or_handle_text(message: types.Message):
    text = message.text.strip().lower()
    user_id = message.from_user.id
    ensure_user_state(user_id)

    if text == "жопа":
        task = users_state[user_id].get("timer_task")
        if task and not task.done():
            task.cancel()
        try:
            await bot.send_message(user_id,
                                   "⏰ Таймер пропущен! Хочешь разбор твоей рекламной кампании?",
                                   reply_markup=kb_start_quiz())
            users_state[user_id]["delayed_sent"] = True
        except Exception:
            pass
        return

# ----------------- Квиз -----------------
@dp.callback_query(lambda c: c.data == "start_quiz")
async def cb_start_quiz(callback: CallbackQuery):
    user_id = callback.from_user.id
    ensure_user_state(user_id)
    users_state[user_id]["quiz"] = {"q_index": 0, "answers": []}
    await send_quiz_question(user_id)
    await callback.answer()

async def send_quiz_question(user_id: int):
    st = users_state.get(user_id)
    if not st:
        return
    q_index = st["quiz"]["q_index"]
    if q_index >= len(QUIZ_QUESTIONS):
        await finalize_quiz(user_id)
        return
    q = QUIZ_QUESTIONS[q_index]
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(opt, callback_data=f"quiz_{q_index}_{i}")] for i, opt in enumerate(q["opts"])]
    )
    await bot.send_message(user_id, q["text"], reply_markup=kb)

@dp.callback_query(lambda c: c.data.startswith("quiz_"))
async def cb_quiz_answer(callback: CallbackQuery):
    user_id = callback.from_user.id
    st = users_state.get(user_id)
    if not st:
        return
    parts = callback.data.split("_")
    if len(parts) != 3:
        return
    q_index, opt_index = int(parts[1]), int(parts[2])
    quiz = st["quiz"]
    while len(quiz["answers"]) <= q_index:
        quiz["answers"].append(None)
    quiz["answers"][q_index] = QUIZ_QUESTIONS[q_index]["opts"][opt_index]
    quiz["q_index"] = q_index + 1
    await callback.answer("Ответ записан.")
    await send_quiz_question(user_id)

async def finalize_quiz(user_id: int):
    st = users_state.get(user_id)
    if not st:
        return
    st["quiz_done"] = True
    trigger_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("💬 Написать менеджеру", url=f"https://t.me/{SELLER_USERNAME.lstrip('@')}")]
    ])
    await bot.send_message(
        user_id,
        "🔔 У тебя нет системной схемы запуска рекламы → вот что тебе нужно…\n\n"
        "Свяжись с менеджером для разбора кампании и подготовки эффективного плана.",
        reply_markup=trigger_kb
    )
    await bot.send_message(NOTIFY_CHAT_ID, f"🟢 Пользователь {user_id} перешёл к менеджеру {SELLER_USERNAME}")

# ----------------- Запуск бота -----------------
async def main():
    print("🤖 Бот запущен и готов.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
