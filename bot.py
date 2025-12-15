import os
import datetime
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
from database import ScheduleDatabase
from keyboards import create_main_menu, create_confirmation_keyboard, create_day_selection_keyboard
from messages import (
    WELCOME_MESSAGE, HELP_MESSAGE,
    format_lesson_message,
    format_day_schedule, format_full_schedule_by_days, format_week_overview
)

# === ОПТИМИЗАЦИЯ НАСТРОЕК ЛОГГИРОВАНИЯ ===
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.WARNING,  # Меньше логов = меньше CPU
    datefmt='%H:%M:%S'
)

# Загрузка токена
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

if not TOKEN:
    print("❌ ОШИБКА: Токен не найден!")
    exit(1)

# Инициализация базы данных (один раз при запуске)
db = ScheduleDatabase()
print("🤖 Бот оптимизирован для минимального потребления CPU")
print(f"📱 Токен: {TOKEN[:10]}...")

# === КЭШИРОВАНИЕ ДАННЫХ ===
_schedule_cache = {}
_cache_timestamp = None
CACHE_TIMEOUT = 300  # 5 минут кэширования


def get_cached_schedule():
    """Кэшируем расписание для экономии запросов к БД"""
    global _schedule_cache, _cache_timestamp

    now = datetime.datetime.now()
    if (_cache_timestamp is None or
            (now - _cache_timestamp).seconds > CACHE_TIMEOUT or
            not _schedule_cache):

        # Обновляем кэш
        _schedule_cache = {}
        days = db.get_all_days_with_lessons()
        for day in days:
            lessons = db.get_lessons_by_day(day)
            if lessons:
                _schedule_cache[day] = lessons
        _cache_timestamp = now
        logging.info("Кэш расписания обновлен")

    return _schedule_cache


def clear_schedule_cache():
    """Очистка кэша (вызывать при изменении расписания)"""
    global _schedule_cache, _cache_timestamp
    _schedule_cache = {}
    _cache_timestamp = None


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start - оптимизированная"""
    user = update.effective_user

    # Используем кэшированные данные
    cached_data = get_cached_schedule()
    days_with_lessons = list(cached_data.keys())
    week_overview = format_week_overview(days_with_lessons)

    keyboard = create_main_menu()

    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n{week_overview}",
        parse_mode='Markdown',
        reply_markup=keyboard
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help - статичный текст, без оптимизации"""
    await update.message.reply_text(HELP_MESSAGE, parse_mode='Markdown')


async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню выбора дня - быстрый отклик"""
    keyboard = create_day_selection_keyboard()
    await update.message.reply_text(
        "📅 Выберите день:",
        reply_markup=keyboard
    )


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на сегодня - с кэшем"""
    days_ru = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    today_idx = datetime.datetime.now().weekday()
    today_ru = days_ru[today_idx]

    # Используем кэш
    cached_data = get_cached_schedule()
    lessons = cached_data.get(today_ru, [])

    if lessons:
        message = f"📅 *{today_ru}:*\n\n"
        for lesson in lessons:
            message += f"• {lesson['time']} - {lesson['subject']}\n"
    else:
        message = f"🎉 *{today_ru}*\nСегодня нет уроков!"

    await update.message.reply_text(message, parse_mode='Markdown')


async def tomorrow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на завтра - с кэшем"""
    days_ru = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    tomorrow_idx = (datetime.datetime.now().weekday() + 1) % 7
    tomorrow_ru = days_ru[tomorrow_idx]

    # Используем кэш
    cached_data = get_cached_schedule()
    lessons = cached_data.get(tomorrow_ru, [])

    if lessons:
        message = f"📅 *{tomorrow_ru}:*\n\n"
        for lesson in lessons:
            message += f"• {lesson['time']} - {lesson['subject']}\n"
    else:
        message = f"📅 *{tomorrow_ru}*\nЗавтра нет уроков!"

    await update.message.reply_text(message, parse_mode='Markdown')


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка inline-кнопок - с кэшем"""
    query = update.callback_query
    await query.answer()

    if query.data.startswith('day_'):
        day = query.data[4:]

        cached_data = get_cached_schedule()

        if day == 'Вся неделя':
            message = format_full_schedule_by_days(cached_data)
        else:
            lessons = cached_data.get(day, [])
            message = format_day_schedule(day, lessons)

        await query.edit_message_text(text=message, parse_mode='Markdown')


async def add_lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавить урок - с очисткой кэша"""
    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "Формат: /add <предмет> <время> <день>\nПример: /add Математика 10:00 Понедельник"
        )
        return

    subject, time, day = context.args[0], context.args[1], context.args[2]
    result = db.add_lesson({'subject': subject, 'time': time, 'day': day})

    if result.get('success'):
        clear_schedule_cache()  # Очищаем кэш при изменении
        await update.message.reply_text(f"✅ '{subject}' добавлен на {day} в {time}")
    else:
        await update.message.reply_text("❌ Ошибка")


async def delete_lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удалить урок - с очисткой кэша"""
    if not context.args:
        await update.message.reply_text("Укажите ID урока: /delete 1")
        return

    try:
        lesson_id = int(context.args[0])
        lesson = db.get_lesson_by_id(lesson_id)

        if not lesson:
            await update.message.reply_text("❌ Урок не найден")
            return

        keyboard = create_confirmation_keyboard(lesson_id)
        await update.message.reply_text(
            f"Удалить:\n{format_lesson_message(lesson)}",
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    except ValueError:
        await update.message.reply_text("❌ Введите число")


async def clear_cache_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Служебная команда для очистки кэша"""
    clear_schedule_cache()
    await update.message.reply_text("✅ Кэш очищен")


def main():
    """Запуск оптимизированного бота"""
    print("🚀 Запуск оптимизированного бота...")

    # Создаем приложение с оптимизированными настройками
    application = Application.builder().token(TOKEN).build()

    # === ОПТИМИЗИРОВАННЫЙ ПОРЯДОК ОБРАБОТЧИКОВ ===
    # Самые частые команды первыми
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("today", today_command))
    application.add_handler(CommandHandler("tomorrow", tomorrow_command))
    application.add_handler(CommandHandler("schedule", schedule_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add", add_lesson_command))
    application.add_handler(CommandHandler("delete", delete_lesson_command))
    application.add_handler(CommandHandler("clearcache", clear_cache_command))  # Новая команда

    # Обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_callback))

    # === ОПТИМИЗИРОВАННЫЙ ЗАПУСК ===
    print("⚡ Оптимизации:")
    print("  • Кэширование расписания (5 мин)")
    print("  • Минимальное логирование")
    print("  • Уменьшены запросы к БД")
    print("  • Статические тексты в памяти")
    print("📝 Напишите /start в Telegram")

    # Оптимизированные параметры polling
    try:
        application.run_polling(
            poll_interval=2.0,  # Увеличен интервал опроса (было 1.0)
            timeout=15,  # Уменьшен таймаут
            drop_pending_updates=True,
            close_loop=False  # Экономит ресурсы
        )
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
    except Exception as e:
        logging.error(f"Ошибка: {e}")

if __name__ == "__main__":
    main()