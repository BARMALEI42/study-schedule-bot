import os
import datetime
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv
from database import ScheduleDatabase
from keyboards import create_main_menu, create_confirmation_keyboard, create_day_selection_keyboard
from messages import (
    WELCOME_MESSAGE, HELP_MESSAGE,
    format_error_message, format_lesson_message,
    format_day_schedule, format_full_schedule_by_days, format_week_overview
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Загрузка токена
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

if not TOKEN:
    print("❌ ОШИБКА: Токен не найден!")
    print("Создайте файл .env с содержимым: BOT_TOKEN=ваш_токен")
    exit(1)

# Инициализация базы данных
db = ScheduleDatabase()
print("✅ База данных инициализирована")
print(f"📱 Токен загружен: {TOKEN[:10]}...")


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user = update.effective_user
    print(f"👤 Пользователь {user.first_name} ({user.id}) запустил бота")

    keyboard = create_main_menu()
    days_with_lessons = db.get_all_days_with_lessons()
    week_overview = format_week_overview(days_with_lessons)

    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n{week_overview}",
        parse_mode='Markdown',
        reply_markup=keyboard
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    await update.message.reply_text(HELP_MESSAGE, parse_mode='Markdown')


async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню выбора дня"""
    keyboard = create_day_selection_keyboard()
    await update.message.reply_text(
        "📅 Выберите день недели:",
        parse_mode='Markdown',
        reply_markup=keyboard
    )


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на сегодня"""
    days_ru = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    today_idx = datetime.datetime.now().weekday()
    today_ru = days_ru[today_idx]

    lessons = db.get_lessons_by_day(today_ru)

    if lessons:
        message = f"📅 *Расписание на сегодня ({today_ru}):*\n\n"
        for lesson in lessons:
            message += f"• *{lesson['time']}* - {lesson['subject']}\n"
    else:
        message = f"🎉 *{today_ru}*\nСегодня нет уроков!"

    await update.message.reply_text(message, parse_mode='Markdown')


async def tomorrow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на завтра"""
    days_ru = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    tomorrow_idx = (datetime.datetime.now().weekday() + 1) % 7
    tomorrow_ru = days_ru[tomorrow_idx]

    lessons = db.get_lessons_by_day(tomorrow_ru)

    if lessons:
        message = f"📅 *Расписание на завтра ({tomorrow_ru}):*\n\n"
        for lesson in lessons:
            message += f"• *{lesson['time']}* - {lesson['subject']}\n"
    else:
        message = f"📅 *{tomorrow_ru}*\nЗавтра нет уроков!"

    await update.message.reply_text(message, parse_mode='Markdown')


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка inline-кнопок"""
    query = update.callback_query
    await query.answer()

    if query.data.startswith('day_'):
        day = query.data[4:]

        if day == 'Вся неделя':
            days = db.get_all_days_with_lessons()
            days_data = {}
            for day_name in days:
                lessons = db.get_lessons_by_day(day_name)
                if lessons:
                    days_data[day_name] = lessons
            message = format_full_schedule_by_days(days_data)
        else:
            lessons = db.get_lessons_by_day(day)
            message = format_day_schedule(day, lessons)

        await query.edit_message_text(text=message, parse_mode='Markdown')


async def add_lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавить урок: /add Математика 10:00 Понедельник"""
    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "Используйте: /add <предмет> <время> <день>\n"
            "Пример: /add Математика 10:00 Понедельник",
            parse_mode='Markdown'
        )
        return

    subject, time, day = context.args[0], context.args[1], context.args[2]
    result = db.add_lesson({'subject': subject, 'time': time, 'day': day})

    if result.get('success'):
        await update.message.reply_text(f"✅ Урок '{subject}' добавлен на {day} в {time}")
    else:
        await update.message.reply_text("❌ Ошибка при добавлении урока")


async def delete_lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удалить урок: /delete 1"""
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
        confirmation_text = f"Удалить урок:\n{format_lesson_message(lesson)}"

        await update.message.reply_text(
            confirmation_text,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    except ValueError:
        await update.message.reply_text("❌ Введите правильный ID (число)")


def main():
    """Запуск бота"""
    print("🚀 Запуск бота...")

    # Создаем приложение
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("schedule", schedule_command))
    application.add_handler(CommandHandler("today", today_command))
    application.add_handler(CommandHandler("tomorrow", tomorrow_command))
    application.add_handler(CommandHandler("add", add_lesson_command))
    application.add_handler(CommandHandler("delete", delete_lesson_command))

    # Обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_callback))

    # Запускаем бота в режиме polling
    print("🤖 Бот запущен. Нажмите Ctrl+C для остановки")
    print("📝 Напишите /start в Telegram")

    try:
        application.run_polling(
            poll_interval=1.0,
            drop_pending_updates=True
        )
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
    except Exception as e:
        print(f"❌ Ошибка: {e}")


if __name__ == "__main__":
    main()