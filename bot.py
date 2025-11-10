import os
# You can now use 'project_dir' as the base path for saving your project files.
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton  # ← добавлен импорт кнопок

# --- Настройка токена ---
bot = Bot(token="8324054424:AAFsS1eHNEom5XpTO3dM2U-NdFIaVkZERX0")  # строка токена в кавычках
dp = Dispatcher()

# --- Обработчик /start ---
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
    """Один раз — форматируем под Markdown (звёздочки/цитаты)."""
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


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Форматируем и отправляем текст
    formatted = format_for_telegram_markdown(welcome_text)
    await message.answer(formatted, parse_mode="Markdown")

    # Отправка файла (проверьте путь)
    guide_path = "files/marketing_manual.pdf"  # <-- здесь внутри функции
    if os.path.exists(guide_path):
        document = FSInputFile(guide_path)
        await message.answer_document(document=document, caption="Вот твой мини-гайд 📖")
    else:
        await message.answer("❌ К сожалению, файл гайда не найден.")

    # Отправляем кнопку на видео
    VIDEO_URL = "https://youtu.be/P-3NZnicpbk"
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🎥 Смотреть урок — Запуск рекламной кампании в Яндекс Директ",
            url=VIDEO_URL
        )]
    ])
    await message.answer(
        "Также мы подготовили обучающее видео, как запустить свою первую рекламную кампанию. Смотри его прямо сейчас 👇",
        reply_markup=kb
    )

# --- Запуск бота ---
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())

