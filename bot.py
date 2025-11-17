import os
import asyncio
from typing import Dict, Any, List
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage

# ----------------- Настройки -----------------
BOT_TOKEN = "8324054424:AAFsS1eHNEom5XpTO3dM2U-NdFIaVkZERX0"
NOTIFY_CHAT_ID = -1003322951241  # чат уведомлений
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
def kb_get_video(): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("🎥 Получить видео", callback_data="get_video")]])
def kb_get_checklist(): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("📑 Получить чек-лист", callback_data="get_checklist")]])
def kb_get_kpi(): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("📊 Получить таблицу KPI", callback_data="get_kpi")]])
def kb_start_quiz(): return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("🧠 Начать квиз", callback_data="start_quiz")]])

QUIZ_QUESTIONS: List[Dict[str, Any]] = [
    {"text": "1) Какая у тебя ниша?", "opts": ["Услуги", "Товары", "Онлайн-школа", "Другое"]},
    {"text": "2) Какую цель ставишь для кампании?", "opts": ["Лиды", "Продажи", "Трафик", "Повышение узнаваемости"]},
    {"text": "3) Опыт в рекламе?", "opts": ["Запускаю впервые", "Настраивал пару раз", "Уверенно работаю", "Я профи"]},
    {"text": "4) Где планируешь запускаться?", "opts": ["Яндекс Директ", "VK / MyTarget", "Meta (Facebook/Instagram)", "Пока не знаю"]}
]

# ----------------- Утилиты -----------------
def ensure_user_state(user_id: int):
    if user_id not in users_state:
        users_state[user_id] = {"step": "started", "timer_task": None, "quiz": {"q_index": 0, "answers": []}}

def get_username_display(user: types.User) -> str:
    return f"@{user.username}" if user.username else user.full_name

# ----------------- Старт бота -----------------
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    ensure_user_state(user_id)

    greeting = (
        "Привет! 👋\nЭто Артем и команда Foton Plus.\n\n"
        "Мы рады приветствовать тебя в нашем образовательном пространстве по маркетингу! 🎯\n"
        "🎁 Первый подарок: мини-гайд, чек-лист, таблица KPI и видео.\n"
        "⚡️ Совет: изучай материалы и применяй — так результат будет быстрее."
    )
    await message.answer(greeting)

    # notify only start
    await bot.send_message(NOTIFY_CHAT_ID, f"✅ {get_username_display(message.from_user)} запустил бота (ID: {user_id})")

    # выдаем материалы по очереди с задержкой
    if os.path.exists(MANUAL_FILE):
        await message.answer_document(FSInputFile(MANUAL_FILE), caption="📘 Мини-мануал")
        await asyncio.sleep(10)
    if os.path.exists(CHECKLIST_FILE):
        await message.answer_document(FSInputFile(CHECKLIST_FILE), caption="📑 Чек-лист")
        await asyncio.sleep(10)
    if os.path.exists(KPI_FILE):
        await message.answer_document(FSInputFile(KPI_FILE), caption="📊 Таблица KPI")
        await asyncio.sleep(10)
    await message.answer("Далее — видео. Нажми кнопку для получения.", reply_markup=kb_get_video())

    users_state[user_id]["step"] = "materials_sent"

# ----------------- Видео -----------------
@dp.callback_query(lambda c: c.data == "get_video")
async def cb_get_video(callback: CallbackQuery):
    user_id = callback.from_user.id
    ensure_user_state(user_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("▶️ Смотреть видео", url=VIDEO_URL)]])
    await callback.message.answer("🎥 Видео-урок: запуск первой рекламной кампании", reply_markup=kb)
    users_state[user_id]["step"] = "video_sent"

    # Schedule delayed message for quiz
    task = users_state[user_id].get("timer_task")
    if task is None or task.done():
        t = asyncio.create_task(schedule_delayed_message(user_id))
        users_state[user_id]["timer_task"] = t

# ----------------- Отложенное сообщение -----------------
async def schedule_delayed_message(user_id: int, delay_seconds: int = DELAY_SECONDS):
    try:
        await asyncio.sleep(delay_seconds)
    except asyncio.CancelledError:
        return

    st = users_state.get(user_id)
    if st is None or st.get("delayed_sent") or st.get("quiz_done"):
        return

    try:
        await bot.send_message(user_id,
                               "⏰ Ты уже посмотрел видео и материалы? Хочешь разбор твоей рекламной кампании?",
                               reply_markup=kb_start_quiz())
        st["delayed_sent"] = True
    except Exception:
        pass

# ----------------- Команда "жопа" пропускает таймер -----------------
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
                                   "⏰ (Тест) Хочешь разбор твоей рекламной кампании?",
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
    if not st: return
    q_index = st["quiz"]["q_index"]
    if q_index >= len(QUIZ_QUESTIONS):
        await finalize_quiz(user_id)
        return
    q = QUIZ_QUESTIONS[q_index]
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(opt, callback_data=f"quiz_{q_index}_{i}")] for i,opt in enumerate(q["opts"])])
    await bot.send_message(user_id, q["text"], reply_markup=kb)

@dp.callback_query(lambda c: c.data.startswith("quiz_"))
async def cb_quiz_answer(callback: CallbackQuery):
    user_id = callback.from_user.id
    st = users_state.get(user_id)
    if not st: return

    parts = callback.data.split("_")
    if len(parts) != 3: return
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
    if not st: return
    answers = st["quiz"].get("answers", [])
    st["quiz_done"] = True

    # Trigger message → переход к менеджеру
    trigger_kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton("💬 Написать менеджеру", url=f"https://t.me/{SELLER_USERNAME.lstrip('@')}")]])
    await bot.send_message(user_id,
                           "🔔 У тебя нет системной схемы запуска рекламы → вот что тебе нужно…\n\n"
                           "Свяжись с менеджером для разбора кампании.",
                           reply_markup=trigger_kb)

    # уведомление только о переходе к менеджеру
    await bot.send_message(NOTIFY_CHAT_ID, f"🟢 Пользователь {user_id} перешёл к менеджеру {SELLER_USERNAME}")

# ----------------- Запуск -----------------
async def main():
    print("🤖 Бот запущен и готов.")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

