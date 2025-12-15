

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