import os
import asyncio
from typing import Dict, Any, List
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage

# ----------------- Настройки -----------------
BOT_TOKEN = "8324054424:AAFsS1eHNEom5XpTO3dM2U-NdFIaVkZERX0"  # <- замени на свой токен если нужно
NOTIFY_CHAT_ID = -1003322951241  # чат куда приходят уведомления
# Ссылки / пути к файлам
VIDEO_URL = "https://youtu.be/P-3NZnicpbk"
MANUAL_FILE = "marketing_manual.pdf"
CHECKLIST_FILE = "check_list.pdf"
KPI_FILE = "metrika.pdf"
# Ссылка на продавца/менеджера (после квиза)
SELLER_USERNAME = "@E_L_0_A_X"
# Длительность отложенного сообщения (в секундах) — 2 часа = 7200
DELAY_SECONDS = 2 * 60 * 60
# Для теста можно временно сделать меньше, но по ТЗ стоит 2 часа.

# ----------------- Инициализация бота -----------------
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# ----------------- Память состояния (вариант B) -----------------
# Структура users_state:
# users_state[user_id] = {
#   "step": "started" | "manual_sent" | "video_sent" | "checklist_sent" | "kpi_sent" | "delayed_sent" | "quiz_done",
#   "timer_task": asyncio.Task | None,
#   "quiz": {
#       "q_index": int,
#       "answers": [str, ...]
#   }
# }
users_state: Dict[int, Dict[str, Any]] = {}

# ----------------- Вспомогательные клавиатуры -----------------
def kb_get_video() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎥 Получить видео", callback_data="get_video")]
    ])

def kb_get_checklist() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📑 Получить чек-лист", callback_data="get_checklist")]
    ])

def kb_get_kpi() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Получить таблицу KPI", callback_data="get_kpi")]
    ])

def kb_start_quiz() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧠 Начать квиз", callback_data="start_quiz")]
    ])

# Вопросы и варианты для квиза
QUIZ_QUESTIONS: List[Dict[str, Any]] = [
    {
        "text": "1) Какая у тебя ниша?",
        "opts": ["Услуги", "Товары", "Онлайн-школа", "Другое"]
    },
    {
        "text": "2) Какую цель ставишь для кампании?",
        "opts": ["Лиды", "Продажи", "Трафик", "Повышение узнаваемости"]
    },
    {
        "text": "3) Опыт в рекламе?",
        "opts": ["Запускаю впервые", "Настраивал пару раз", "Уверенно работаю", "Я профи"]
    },
    {
        "text": "4) Где планируешь запускаться?",
        "opts": ["Яндекс Директ", "VK / MyTarget", "Meta (Facebook/Instagram)", "Пока не знаю"]
    }
]

# ----------------- Утилиты -----------------
def ensure_user_state(user_id: int):
    if user_id not in users_state:
        users_state[user_id] = {
            "step": "started",
            "timer_task": None,
            "quiz": {"q_index": 0, "answers": []}
        }

def get_username_display(user: types.User) -> str:
    return f"@{user.username}" if user.username else user.full_name

# ----------------- Основная логика выдачи материалов -----------------
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    ensure_user_state(user_id)

    # greeting
    await message.answer(
        "Привет! 👋\n" "Это Артем и команда Foton Plus.\n\n" 
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

    # send manual
    if os.path.exists(MANUAL_FILE):
        await message.answer_document(FSInputFile(MANUAL_FILE), caption="📘 Мини-мануал — стартовый материал")
    else:
        await message.answer("❌ Файл мини-мануала не найден на сервере.")

    users_state[user_id]["step"] = "manual_sent"
    # notify admin/chat
    await bot.send_message(NOTIFY_CHAT_ID,
                           f"✅ {get_username_display(message.from_user)} запустил бота и получил мини-мануал (ID: {user_id})")

    # button for video
    await message.answer("Далее — видео. Нажми кнопку, чтобы получить его.", reply_markup=kb_get_video())

# === Получить видео (по кнопке) ===
@dp.callback_query(lambda c: c.data == "get_video")
async def cb_get_video(callback: CallbackQuery):
    user_id = callback.from_user.id
    ensure_user_state(user_id)

    # send video link as button
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="▶️ Смотреть видео", url=VIDEO_URL)]
    ])
    await callback.message.answer("🎥 Видео-урок: запуск первой рекламной кампании", reply_markup=kb)

    users_state[user_id]["step"] = "video_sent"
    await bot.send_message(NOTIFY_CHAT_ID,
                           f"🎬 {get_username_display(callback.from_user)} получил видео (ID: {user_id})")

    # Provide next button (checklist) after video
    await callback.message.answer("Готов перейти к чек-листу? Нажми кнопку ниже.", reply_markup=kb_get_checklist())

# === Получить чек-лист (по кнопке) ===
@dp.callback_query(lambda c: c.data == "get_checklist")
async def cb_get_checklist(callback: CallbackQuery):
    user_id = callback.from_user.id
    ensure_user_state(user_id)

    if os.path.exists(CHECKLIST_FILE):
        await callback.message.answer_document(FSInputFile(CHECKLIST_FILE),
                                              caption="📑 Чек-лист: проверка рекламной кампании перед запуском")
    else:
        await callback.message.answer("❌ Файл чек-листа не найден на сервере.")

    users_state[user_id]["step"] = "checklist_sent"
    await bot.send_message(NOTIFY_CHAT_ID,
                           f"📑 {get_username_display(callback.from_user)} скачал чек-лист (ID: {user_id})")

    # Next button for KPI
    await callback.message.answer("Последний файл — таблица KPI. Нажми кнопку, чтобы получить.", reply_markup=kb_get_kpi())

# === Получить KPI (по кнопке) ===
@dp.callback_query(lambda c: c.data == "get_kpi")
async def cb_get_kpi(callback: CallbackQuery):
    user_id = callback.from_user.id
    ensure_user_state(user_id)

    if os.path.exists(KPI_FILE):
        await callback.message.answer_document(FSInputFile(KPI_FILE), caption="📊 Таблица KPI для анализа кампаний")
    else:
        await callback.message.answer("❌ Файл таблицы KPI не найден на сервере.")

    users_state[user_id]["step"] = "kpi_sent"
    await bot.send_message(NOTIFY_CHAT_ID,
                           f"📊 {get_username_display(callback.from_user)} скачал KPI (ID: {user_id})")

    # after KPI: schedule delayed message (if not already scheduled)
    task = users_state[user_id].get("timer_task")
    if task is None or task.done():
        # store and create task
        t = asyncio.create_task(schedule_delayed_message(user_id))
        users_state[user_id]["timer_task"] = t
        await callback.message.answer("Отлично — материалы выданы. Удачи в изучении!")
    else:
        await callback.message.answer("Напоминание уже запланировано — ждём уведомления.")

# ----------------- Отложенное сообщение + запуск квиза -----------------
async def schedule_delayed_message(user_id: int, delay_seconds: int = DELAY_SECONDS):
    """
    Ждём delay_seconds, затем отправляем отложенное сообщение с кнопкой "Начать квиз".
    Если пользователь в users_state на момент отправки уже имеет 'delayed_sent' или 'quiz_done', ничего не делаем.
    """
    # wait
    try:
        await asyncio.sleep(delay_seconds)
    except asyncio.CancelledError:
        return

    # double-check user state
    st = users_state.get(user_id)
    if st is None:
        return

    # don't resend if already done
    if st.get("delayed_sent") or st.get("quiz_done"):
        return

    # try to send message to user
    try:
        await bot.send_message(user_id,
                               "⏰ Ты уже посмотрел видео и материалы к нему? Хочешь разбор твоей рекламной кампании?",
                               reply_markup=kb_start_quiz())
        st["delayed_sent"] = True
        # notify admin
        await bot.send_message(NOTIFY_CHAT_ID,
                               f"⏰ Напоминание отправлено пользователю {user_id}")
    except Exception as e:
        # can't send (user blocked bot etc.) — log to admin
        await bot.send_message(NOTIFY_CHAT_ID, f"⚠️ Не удалось отправить напоминание {user_id}: {e}")

# ----------------- Пропустить ожидание: команда "жопа" -----------------
@dp.message()
async def skip_timer_or_handle_text(message: types.Message):
    text = message.text.strip().lower()
    user_id = message.from_user.id
    ensure_user_state(user_id)

    # if user types the magic word "жопа" -> immediately send delayed message + start quiz
    if text == "жопа":
        # cancel existing timer if any
        task = users_state[user_id].get("timer_task")
        if task and not task.done():
            task.cancel()

        # send delayed prompt immediately (same as schedule_delayed_message)
        try:
            await bot.send_message(user_id,
                                   "⏰ (Тест) ы уже посмотрел видео и материалы к нему? Хочешь разбор твоей рекламной кампании?",
                                   reply_markup=kb_start_quiz())
            users_state[user_id]["delayed_sent"] = True
            await bot.send_message(NOTIFY_CHAT_ID, f"🟢 Пользователь {user_id} использовал 'жопа' — напоминание отправлено сразу.")
        except Exception as e:
            await bot.send_message(NOTIFY_CHAT_ID, f"⚠️ Ошибка при 'жопа' для {user_id}: {e}")

        return

    # Если пришёл любой другой текст — не мешаем; оставляем для будущих расширений
    # Можно обрабатывать команды/чат отдельно
    # (иначе бот будет игнорировать обычные сообщения)
    return

# ----------------- Обработка начала квиза -----------------
@dp.callback_query(lambda c: c.data == "start_quiz")
async def cb_start_quiz(callback: CallbackQuery):
    user_id = callback.from_user.id
    ensure_user_state(user_id)

    # initialize quiz
    users_state[user_id]["quiz"] = {"q_index": 0, "answers": []}
    users_state[user_id]["quiz_started"] = True

    # send first question
    await send_quiz_question(user_id)

    # acknowledge callback
    await callback.answer()

async def send_quiz_question(user_id: int):
    st = users_state.get(user_id)
    if not st:
        return

    q_index = st["quiz"]["q_index"]
    if q_index >= len(QUIZ_QUESTIONS):
        # quiz finished
        await finalize_quiz(user_id)
        return

    q = QUIZ_QUESTIONS[q_index]
    text = q["text"]
    opts = q["opts"]
    # build keyboard
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=opt, callback_data=f"quiz_{q_index}_{i}")]
                         for i, opt in enumerate(opts)]
    )
    try:
        await bot.send_message(user_id, text, reply_markup=kb)
    except Exception as e:
        await bot.send_message(NOTIFY_CHAT_ID, f"⚠️ Не удалось отправить вопрос квиза {user_id}: {e}")

# quiz answer handler
@dp.callback_query(lambda c: c.data.startswith("quiz_"))
async def cb_quiz_answer(callback: CallbackQuery):
    user_id = callback.from_user.id
    ensure_user_state(user_id)

    data = callback.data  # e.g. "quiz_0_2"
    parts = data.split("_")
    if len(parts) != 3:
        await callback.answer("Некорректный ответ.")
        return

    q_index = int(parts[1])
    opt_index = int(parts[2])

    st = users_state[user_id]
    quiz = st.get("quiz")
    if not quiz:
        await callback.answer("Квиз не запущен.")
        return

    # record answer
    # ensure answers list is of proper length
    if len(quiz["answers"]) <= q_index:
        # extend to fit
        while len(quiz["answers"]) <= q_index:
            quiz["answers"].append(None)
    quiz["answers"][q_index] = QUIZ_QUESTIONS[q_index]["opts"][opt_index]

    # move to next question
    quiz["q_index"] = q_index + 1
    await callback.answer("Ответ записан.")

    # send next or finalize
    await send_quiz_question(user_id)

# finalize quiz
async def finalize_quiz(user_id: int):
    st = users_state.get(user_id)
    if not st:
        return

    answers = st["quiz"].get("answers", [])
    st["quiz_done"] = True
    st["quiz_started"] = False

    # prepare summary
    summary_lines = ["🧾 Результаты квиза:"]
    for idx, q in enumerate(QUIZ_QUESTIONS):
        ans = answers[idx] if idx < len(answers) and answers[idx] is not None else "—"
        summary_lines.append(f"{q['text']} ➜ {ans}")
    summary_text = "\n".join(summary_lines)

    # send summary to user
    try:
        await bot.send_message(user_id, "Спасибо! Вот твои ответы:\n\n" + summary_text)
    except Exception:
        pass

    # send summary to admin chat / notify
    try:
        await bot.send_message(NOTIFY_CHAT_ID,
                               f"🧾 Квиз пройден пользователем {user_id}:\n\n{summary_text}")
    except Exception:
        pass

    # send trigger message with link to seller
    try:
        trigger_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💬 Написать менеджеру", url=f"https://t.me/{SELLER_USERNAME.lstrip('@')}")]
        ])
        await bot.send_message(user_id,
                               "🔔 У тебя нет системной схемы запуска рекламы → вот что тебе нужно…\n\n"
                               "Свяжись с нашим менеджером для разбора — он поможет подготовить эффективный план продвижения твоей РК.",
                               reply_markup=trigger_kb)
    except Exception as e:
        await bot.send_message(NOTIFY_CHAT_ID, f"⚠️ Не удалось отправить триггер {user_id}: {e}")

# ----------------- Graceful shutdown handler (optional) -----------------
# При перезапуске/остановке процесса в памяти ничего не сохранится.
# Можно добавить обработку signal'ов для отмены тасков, если нужно.

# ----------------- Запуск бота -----------------
async def main():
    print("🤖 Бот запущен (вариант B — память в процессе).")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
