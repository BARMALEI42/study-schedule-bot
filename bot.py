
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv
from database import ScheduleDatabase


load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
db = ScheduleDatabase()


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Базовая логика
    await update.message.reply_text("Привет! Я бот расписания.")


async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # получаете данные из БД
    lessons = db.get_all_lessons()
    # Дальше передаёте напарнику для форматирования


async def add_lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # валидируете и сохраняете в БД
    if not context.args or len(context.args) < 3:
        return  # Ошибка

    subject, time, day = context.args[0], context.args[1], context.args[2]
    result = db.add_lesson({'subject': subject, 'time': time, 'day': day})


async def delete_lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    #работаете с БД
    if context.args:
        lesson_id = int(context.args[0])
        db.delete_lesson(lesson_id)


def main():
    # настраиваете Application
    application = Application.builder().token(TOKEN).build()

    # добавляете обработчики
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("schedule", schedule_command))
    application.add_handler(CommandHandler("add", add_lesson_command))
    application.add_handler(CommandHandler("delete", delete_lesson_command))

    # запускаете бота
    application.run_polling()
=======
from keyboards import create_main_menu, create_confirmation_keyboard
from messages import (
    WELCOME_MESSAGE, HELP_MESSAGE,
    format_schedule_message, format_error_message, format_lesson_message  # Добавлена функция
)

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
    # Вы получаете данные
    lessons = db.get_all_lessons()
    message = format_schedule_message(lessons)
    await update.message.reply_text(message, parse_mode='Markdown')

async def delete_lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Укажите ID урока для удаления. Пример: /delete_lesson 1",
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
>>>>>>> fronted/add-commands
