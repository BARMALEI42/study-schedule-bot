import os
import datetime
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

load_dotenv()
TOKEN = os.getenv('8598621466:AAEHM1KtekvccU8GIr0CdJS_p3KiHM5IXZc')
db = ScheduleDatabase()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Улучшенный старт с клавиатурой и обзором недели"""
    keyboard = create_main_menu()

    # Получаем дни с уроками для обзора недели
    days_with_lessons = db.get_all_days_with_lessons()
    week_overview = format_week_overview(days_with_lessons)

    welcome_text = f"{WELCOME_MESSAGE}\n\n{week_overview}"

    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=keyboard
    )


async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню выбора дня для просмотра расписания"""
    keyboard = create_day_selection_keyboard()
    await update.message.reply_text(
        "📅 *Выберите день недели:*",
        parse_mode='Markdown',
        reply_markup=keyboard
    )


async def schedule_by_day_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать расписание на конкретный день (/schedule_понедельник)"""
    command_text = update.message.text.lower()

    # Определяем день из команды
    days_mapping = {
        'понедельник': 'Понедельник',
        'вторник': 'Вторник',
        'среда': 'Среда',
        'четверг': 'Четверг',
        'пятница': 'Пятница',
        'суббота': 'Суббота',
        'воскресенье': 'Воскресенье'
    }

    for ru_day, db_day in days_mapping.items():
        if ru_day in command_text:
            lessons = db.get_lessons_by_day(db_day)
            message = format_day_schedule(db_day, lessons)
            await update.message.reply_text(message, parse_mode='Markdown')
            return

    # Если день не указан, показываем меню выбора
    await schedule_command(update, context)


async def show_full_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать полное расписание на всю неделю"""
    days = db.get_all_days_with_lessons()
    days_data = {}

    for day in days:
        lessons = db.get_lessons_by_day(day)
        if lessons:
            days_data[day] = lessons

    message = format_full_schedule_by_days(days_data)
    await update.message.reply_text(message, parse_mode='Markdown')


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать расписание на сегодня"""
    # Русские названия дней недели
    days_ru = {
        0: 'Понедельник',
        1: 'Вторник',
        2: 'Среда',
        3: 'Четверг',
        4: 'Пятница',
        5: 'Суббота',
        6: 'Воскресенье'
    }

    today = datetime.datetime.now().weekday()  # 0=понедельник, 6=воскресенье
    today_ru = days_ru.get(today, 'Понедельник')

    lessons = db.get_lessons_by_day(today_ru)

    if lessons:
        message = f"📅 *Расписание на сегодня ({today_ru}):*\n\n"
        for lesson in lessons:
            message += f"• *{lesson['time']}* - {lesson['subject']} (ID: {lesson['id']})\n"
    else:
        message = f"🎉 *{today_ru}*\nСегодня нет уроков! Можно отдыхать!"

    await update.message.reply_text(message, parse_mode='Markdown')


async def tomorrow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать расписание на завтра"""
    days_ru = {
        0: 'Понедельник',
        1: 'Вторник',
        2: 'Среда',
        3: 'Четверг',
        4: 'Пятница',
        5: 'Суббота',
        6: 'Воскресенье'
    }

    tomorrow = (datetime.datetime.now().weekday() + 1) % 7
    tomorrow_ru = days_ru.get(tomorrow, 'Понедельник')

    lessons = db.get_lessons_by_day(tomorrow_ru)

    if lessons:
        message = f"📅 *Расписание на завтра ({tomorrow_ru}):*\n\n"
        for lesson in lessons:
            message += f"• *{lesson['time']}* - {lesson['subject']} (ID: {lesson['id']})\n"
    else:
        message = f"📅 *{tomorrow_ru}*\nЗавтра нет уроков!"

    await update.message.reply_text(message, parse_mode='Markdown')


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий на inline-кнопки (выбор дня)"""
    query = update.callback_query
    await query.answer()

    if query.data.startswith('day_'):
        day = query.data[4:]  # Убираем 'day_'

        if day == 'Вся неделя':
            # Показать всю неделю
            days = db.get_all_days_with_lessons()
            days_data = {}

            for day_name in days:
                lessons = db.get_lessons_by_day(day_name)
                if lessons:
                    days_data[day_name] = lessons

            message = format_full_schedule_by_days(days_data)
        else:
            # Показать конкретный день
            lessons = db.get_lessons_by_day(day)
            message = format_day_schedule(day, lessons)

        await query.edit_message_text(
            text=message,
            parse_mode='Markdown'
        )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать статистику расписания"""
    stats = db.get_stats()

    message = (
        "📊 *Статистика вашего расписания:*\n\n"
        f"• Всего уроков: *{stats['total_lessons']}*\n"
        f"• Дней с уроками: *{stats['days_with_lessons']}*\n"
        f"• Разных предметов: *{stats['subjects_count']}*\n"
    )

    if stats['most_busy_day']:
        message += f"• Самый загруженный день: *{stats['most_busy_day']}*\n"

    await update.message.reply_text(message, parse_mode='Markdown')


async def clear_day_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очистить все уроки в указанный день"""
    if not context.args:
        await update.message.reply_text(
            "Укажите день для очистки. Пример: /clear Понедельник\n"
            "Доступные дни: Понедельник, Вторник, Среда, Четверг, Пятница, Суббота, Воскресенье",
            parse_mode='Markdown'
        )
        return

    day = context.args[0].capitalize()
    valid_days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']

    if day not in valid_days:
        await update.message.reply_text(
            f"❌ Неверный день. Используйте: {', '.join(valid_days)}",
            parse_mode='Markdown'
        )
        return

    # Получаем уроки перед удалением
    lessons_before = db.get_lessons_by_day(day)

    if not lessons_before:
        await update.message.reply_text(
            f"📅 В *{day}* и так нет уроков.",
            parse_mode='Markdown'
        )
        return

    # Удаляем
    deleted_count = len(lessons_before)
    success = db.clear_day(day)

    if success:
        message = (
            f"🗑️ *Удалено {deleted_count} уроков из {day}:*\n\n"
        )
        for lesson in lessons_before:
            message += f"• {lesson['time']} - {lesson['subject']}\n"

        await update.message.reply_text(message, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Ошибка при удалении уроков", parse_mode='Markdown')


# Остальные функции (add_lesson_command, delete_lesson_command, help_command)
# остаются без изменений, копируем их как есть:

async def add_lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление урока"""
    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "Используйте: /add <предмет> <время> <день>\nПример: /add Математика 10:00 Понедельник",
            parse_mode='Markdown'
        )
        return

    subject, time, day = context.args[0], context.args[1], context.args[2]
    result = db.add_lesson({'subject': subject, 'time': time, 'day': day})

    if result.get('success'):
        await update.message.reply_text(f"✅ Урок '{subject}' добавлен на {day} в {time} (ID: {result['lesson_id']})")
    else:
        await update.message.reply_text("❌ Ошибка при добавлении урока")


async def delete_lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удаление урока с подтверждением"""
    if not context.args:
        await update.message.reply_text(
            "Укажите ID урока для удаления. Пример: /delete 1",
            parse_mode='Markdown'
        )
        return

    try:
        lesson_id = int(context.args[0])
        lesson = db.get_lesson_by_id(lesson_id)

        if not lesson:
            await update.message.reply_text(format_error_message('lesson not found'))
            return

        keyboard = create_confirmation_keyboard(lesson_id)

        confirmation_text = (
            f'**Подтверждение удаления**\n\n'
            f'{format_lesson_message(lesson)}\n\n'
            f'Вы уверены, что хотите удалить этот урок?'
        )

        await update.message.reply_text(
            confirmation_text,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    except ValueError:
        await update.message.reply_text(format_error_message('time_format'))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда помощи"""
    await update.message.reply_text(
        HELP_MESSAGE,
        parse_mode='Markdown'
    )


def main():
    """Основная функция запуска бота"""
    application = Application.builder().token(TOKEN).build()

    # Основные команды
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))

    # Команды расписания
    application.add_handler(CommandHandler("schedule", schedule_command))
    application.add_handler(CommandHandler("today", today_command))
    application.add_handler(CommandHandler("tomorrow", tomorrow_command))
    application.add_handler(CommandHandler("week", show_full_schedule))
    application.add_handler(CommandHandler("clear", clear_day_command))

    # Команды работы с уроками
    application.add_handler(CommandHandler("add", add_lesson_command))
    application.add_handler(CommandHandler("delete", delete_lesson_command))

    # Обработчик inline-кнопок (выбор дня)
    application.add_handler(CallbackQueryHandler(button_callback))

    # Обработчик команд вида /schedule_понедельник
    application.add_handler(MessageHandler(
        filters.Regex(r'^/schedule_'),
        schedule_by_day_command
    ))

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()


def main():
    """Основная функция запуска бота"""
    application = Application.builder().token(TOKEN).build()

    # ... все ваши обработчики ...

    # Запускаем бота
    print("Бот запущен...")

    # Для PythonAnywhere используем webhook
    if os.getenv('PYTHONANYWHERE_DOMAIN'):
        # Webhook для продакшена
        domain = os.getenv('PYTHONANYWHERE_DOMAIN', 'www.pythonanywhere.com')
        webhook_url = f"https://{domain}/{TOKEN}"

        application.run_webhook(
            listen="0.0.0.0",
            port=8444,  # PythonAnywhere использует порт 5000
            url_path=TOKEN,
            webhook_url=webhook_url,
            secret_token='WEBHOOK_SECRET'
        )
    else:
        # Polling для локальной разработки
        application.run_polling()

if __name__ == "__main__":
    main()