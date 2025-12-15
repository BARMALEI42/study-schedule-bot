import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
from database import ScheduleDatabase
from keyboards import create_main_menu, create_confirmation_keyboard
from messages import (
    WELCOME_MESSAGE, HELP_MESSAGE,
    format_schedule_message, format_error_message, format_lesson_message
)

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
db = ScheduleDatabase()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Улучшенный старт с клавиатурой"""
    keyboard = create_main_menu()
    await update.message.reply_text(
        WELCOME_MESSAGE,
        parse_mode='Markdown',
        reply_markup=keyboard
    )


async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Красивое отображение расписания"""
    lessons = db.get_all_lessons()
    message = format_schedule_message(lessons)
    await update.message.reply_text(message, parse_mode='Markdown')


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

    if result:
        await update.message.reply_text(f"✅ Урок '{subject}' добавлен на {day} в {time}")
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

    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("schedule", schedule_command))
    application.add_handler(CommandHandler("add", add_lesson_command))
    application.add_handler(CommandHandler("delete", delete_lesson_command))
    application.add_handler(CommandHandler("help", help_command))

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()


if __name__ == "__main__":
    main()