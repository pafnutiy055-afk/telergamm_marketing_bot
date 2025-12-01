#!/usr/bin/env python3
# coding: utf-8

import os
import asyncio
import logging
from typing import Optional

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

# -----------------------
# Настройка логирования
# -----------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("automaton_bot")

# -----------------------
# Конфигурация
# -----------------------
BOT_TOKEN = "8324054424:AAFsS1eHNEom5XpTO3dM2U-NdFIaVkZERX0"  # Замените на свой токен при деплое
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Чат менеджеров/админов (группа или личный чат)
NOTIFY_CHAT_ID = -1003322951241  # <-- замените на свой ID

# Хранилище состояний (когда ожидаем вопрос от пользователя)
user_state = {}

# -----------------------
# Маркетинговая цель и тон
# -----------------------
# Маркетинговая цель:
# Прогреть клиента, выдать бесплатные материалы (мануал, чек-лист),
# подготовить к целевому действию: заказ рекламы / вступление в закрытый канал.

# Tone of voice: деловой, дружелюбный, уважительный, молодежный.

# -----------------------
# Тексты сообщений (продающие)
# -----------------------
TEXT_WELCOME = (
    "👋 *Привет!* Это *Артём* и команда *Foton Plus* — помогаем бизнесу "
    "запускать рекламу, которая приносит прибыль.\n\n"
    "Выбери, что тебе нужно — все важные материалы под рукой."
)

TEXT_ABOUT = (
    "ℹ️ *О компании Foton Plus*\n\n"
    "Мы — команда маркетологов и таргетологов с практикой реальных запусков.\n"
    "Даем не шаблоны, а рабочие решения: аудит, запуск, оптимизация.\n\n"
    "Хочешь быстрый аудит? Забирай чек-лист и присылай данные менеджеру."
)

TEXT_TARIFFS = (
    "🚀 *Тарифы и услуги (кратко):*\n\n"
    "• Запуск «под ключ» — от *19 900 ₽*\n"
    "• Ретаргетинг и аудит — от *3 900 ₽*\n"
    "• Ведение рекламы — от *14 900 ₽/мес*\n\n"
    "Нужна консультация? Нажми кнопку связи с менеджером."
)

TEXT_ASK_QUESTION_PROMPT = (
    "✉️ Напиши свой вопрос прямо сюда — менеджер получит сообщение и ответит.\n\n"
    "_Пожалуйста, кратко опиши нишу, канал продаж и желаемую цель._"
)

VIDEO_URL = "https://youtu.be/P-3NZnicpbk"

# -----------------------
# UI: главное меню (ReplyKeyboard) и CTA (InlineKeyboard)
# -----------------------
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📘 Получить мануал"), KeyboardButton(text="📊 KPI таблица")],
        [KeyboardButton(text="📑 Чек-лист"), KeyboardButton(text="🎥 Смотреть видео")],
        [KeyboardButton(text="ℹ️ Узнать о нас"), KeyboardButton(text="❓ Задать вопрос")],
        [KeyboardButton(text="🚀 Тарифы")],
    ],
    resize_keyboard=True
)

btn_contact_manager = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📩 Написать менеджеру", url="https://t.me/bery_lydu")]
])

btn_watch_video = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="▶️ Смотреть урок", url=VIDEO_URL)]
])

# -----------------------
# Вспомогательные функции согласно AUTOMAT
# -----------------------

async def notify(action: str, user: types.User):
    """
    Observer: отправляет мгновенное уведомление в менеджерский чат.
    Формат: "🔔 [Действие] | 👤 @username"
    """
    try:
        username = f"@{user.username}" if user.username else user.full_name
        text = f"🔔 {action} | 👤 {username}"
        await bot.send_message(NOTIFY_CHAT_ID, text)
        logger.info("Notified managers: %s", text)
    except Exception as e:
        logger.exception("Failed to send notify message: %s", e)


async def humanize_send_text(chat_id: int, text: str):
    """
    Humanize: перед отправкой текста имитируем печать и делаем паузу
    в зависимости от длины текста (минимум 0.5 сек).
    """
    try:
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
    except Exception:
        # На некоторых типах чатов действие может не отправляться — не критично
        pass

    # пауза: минимум 0.5 сек + 0.01 сек на символ (ограничим)
    pause = max(0.5, min(1.5, 0.005 * len(text) + 0.3))
    await asyncio.sleep(pause)


async def humanize_send_file(chat_id: int):
    """
    Humanize before sending a file: show upload action and sleep a bit longer.
    """
    try:
        await bot.send_chat_action(chat_id=chat_id, action=ChatAction.UPLOAD_DOCUMENT)
    except Exception:
        pass
    await asyncio.sleep(0.7)


def safe_file_exists(path: str) -> bool:
    """
    Safe-Send: проверяем наличие файла локально перед отправкой
    """
    exists = os.path.exists(path)
    if not exists:
        logger.warning("File not found: %s", path)
    return exists

# -----------------------
# Хендлеры бота (меню)
# -----------------------

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    /start - приветствие и меню. Отправляет уведомление менеджеру.
    """
    try:
        await humanize_send_text(message.chat.id, TEXT_WELCOME)
        await message.answer(TEXT_WELCOME, reply_markup=main_menu, parse_mode="Markdown")
        # Уведомление менеджерам
        await notify("Открыл бота", message.from_user)
    except Exception as e:
        logger.exception("Error in /start handler: %s", e)
        # Нежная заглушка пользователю
        await message.answer("Произошла ошибка — попробуйте позже.")

# ---- Получить мануал ----
@dp.message(F.text == "📘 Получить мануал")
async def cmd_manual(message: types.Message):
    action = "Запросил мануал"
    await notify(action, message.from_user)

    path = "marketing_manual.pdf"
    if safe_file_exists(path):
        try:
            await humanize_send_file(message.chat.id)
            await message.answer_document(FSInputFile(path), caption="📘 *Твой Мануал по маркетингу*", parse_mode="Markdown")
        except Exception as e:
            logger.exception("Failed to send manual: %s", e)
            await message.answer("Извините, не удалось отправить файл. Попробуйте позже.")
    else:
        # аккуратная заглушка
        await humanize_send_text(message.chat.id, "⚠️ Файл временно недоступен.")
        await message.answer("⚠️ Файл *marketing_manual.pdf* временно недоступен. Свяжись с менеджером.", parse_mode="Markdown", reply_markup=btn_contact_manager)

# ---- KPI таблица ----
@dp.message(F.text == "📊 KPI таблица")
async def cmd_kpi(message: types.Message):
    action = "Запросил KPI таблицу"
    await notify(action, message.from_user)

    path = "metrika.pdf"
    if safe_file_exists(path):
        try:
            await humanize_send_file(message.chat.id)
            await message.answer_document(FSInputFile(path), caption="📊 *Таблица KPI (метрика)*", parse_mode="Markdown")
        except Exception as e:
            logger.exception("Failed to send KPI file: %s", e)
            await message.answer("Не удалось отправить KPI таблицу — попробуй позже.")
    else:
        await humanize_send_text(message.chat.id, "⚠️ Файл временно недоступен.")
        await message.answer("⚠️ Файл *metrika.pdf* отсутствует на сервере.", parse_mode="Markdown")

# ---- Чек-лист ----
@dp.message(F.text == "📑 Чек-лист")
async def cmd_checklist(message: types.Message):
    action = "Запросил чек-лист"
    await notify(action, message.from_user)

    path = "check_list.pdf"
    if safe_file_exists(path):
        try:
            await humanize_send_file(message.chat.id)
            await message.answer_document(FSInputFile(path), caption="📑 *Чек-лист: Проверка кампании*", parse_mode="Markdown")
        except Exception as e:
            logger.exception("Failed to send checklist: %s", e)
            await message.answer("Не удалось отправить чек-лист — попробуйте позже.")
    else:
        await humanize_send_text(message.chat.id, "⚠️ Файл временно недоступен.")
        await message.answer("⚠️ Файл *check_list.pdf* отсутствует.", parse_mode="Markdown")

# ---- Смотреть видео ----
@dp.message(F.text == "🎥 Смотреть видео")
async def cmd_video(message: types.Message):
    action = "Открыл видео"
    await notify(action, message.from_user)

    try:
        await humanize_send_text(message.chat.id, "Готовлю видео...")
        await message.answer("🎥 *Видеоурок:* посмотри концентрат стратегий и примеров.", parse_mode="Markdown", reply_markup=btn_watch_video)
    except Exception as e:
        logger.exception("Failed to send video CTA: %s", e)
        await message.answer("Не удалось показать видео — попробуй позже.")

# ---- Узнать о нас ----
@dp.message(F.text == "ℹ️ Узнать о нас")
async def cmd_about(message: types.Message):
    action = "Открыл информацию о компании"
    await notify(action, message.from_user)

    try:
        await humanize_send_text(message.chat.id, TEXT_ABOUT)
        # inline: связь с менеджером
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📩 Связаться с менеджером", url="https://t.me/bery_lydu")]
        ])
        await message.answer(TEXT_ABOUT, parse_mode="Markdown", reply_markup=kb)
    except Exception as e:
        logger.exception("Failed to send about text: %s", e)
        await message.answer("Произошла ошибка, попробуйте позже.")

# ---- Задать вопрос ----
@dp.message(F.text == "❓ Задать вопрос")
async def cmd_ask_question(message: types.Message):
    action = "Хочет задать вопрос"
    await notify(action, message.from_user)

    # Перевод в состояние ожидания вопроса
    user_state[message.from_user.id] = {"awaiting_question": True}
    try:
        await humanize_send_text(message.chat.id, TEXT_ASK_QUESTION_PROMPT)
        await message.answer(TEXT_ASK_QUESTION_PROMPT, parse_mode="Markdown")
    except Exception as e:
        logger.exception("Failed to prompt for question: %s", e)
        await message.answer("Произошла ошибка, повторите позже.")

# ---- Тарифы ----
@dp.message(F.text == "🚀 Тарифы")
async def cmd_tariffs(message: types.Message):
    action = "Открыл тарифы"
    await notify(action, message.from_user)

    try:
        await humanize_send_text(message.chat.id, TEXT_TARIFFS)
        await message.answer(TEXT_TARIFFS, parse_mode="Markdown", reply_markup=btn_contact_manager)
    except Exception as e:
        logger.exception("Failed to send tariffs: %s", e)
        await message.answer("Не удалось показать тарифы — попробуйте позже.")

# -----------------------
# Общий обработчик текста: ловим вопросы и нештатные сообщения
# -----------------------
@dp.message(F.text)
async def catch_all_text(message: types.Message):
    """
    Этот обработчик ловит:
    - Ответ пользователя на приглашение 'Задать вопрос' (если ожидаем)
    - Любой другой свободный текст — отправляем подсказку и меню
    """
    uid = message.from_user.id

    # Если ожидаем вопрос от пользователя
    if uid in user_state and user_state[uid].get("awaiting_question"):
        question_text = message.text.strip()
        # Отправляем менеджеру уведомление с вопросом (включая текст вопроса)
        try:
            username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.full_name
            notify_text = f"📨 Вопрос от {username} | {question_text}"
            # уведомляем менеджеров
            await bot.send_message(NOTIFY_CHAT_ID, notify_text)
            logger.info("Forwarded user question to managers: %s", notify_text)
            # Отвечаем пользователю
            await humanize_send_text(message.chat.id, "Спасибо! Менеджер скоро свяжется.")
            await message.answer("✅ Спасибо! Твой вопрос отправлен менеджеру. Ожидай ответ в чате или напиши менеджеру напрямую.", reply_markup=main_menu)
        except Exception as e:
            logger.exception("Failed to forward question: %s", e)
            await message.answer("Не удалось отправить вопрос. Попробуй позже.", reply_markup=main_menu)
        finally:
            # Убираем состояние ожидания
            user_state.pop(uid, None)
        return

    # Если текст не распознан — даём подсказку и меню
    try:
        await humanize_send_text(message.chat.id, "Я могу показать главное меню — выбирай кнопку.")
        await message.answer("Нажми кнопку в меню ниже, чтобы получить материал или задать вопрос.", reply_markup=main_menu)
        await notify("Отправил меню по нераспознанному сообщению", message.from_user)
    except Exception as e:
        logger.exception("Failed in catch-all handler: %s", e)

# -----------------------
# Запуск бота
# -----------------------
async def main():
    logger.info("Бот запускается...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception:
        logger.debug("Webhook delete skipped or failed.")
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception("Polling stopped with exception: %s", e)
    finally:
        logger.info("Бот завершил работу.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен вручную.")
