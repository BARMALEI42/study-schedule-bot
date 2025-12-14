from keyboards import create_main_menu, create_confirmation_keyboard
from messages import (
    WELCOME_MESSAGE, HELP_MESSAGE,
    format_sсhedule_message, foramt_error_message)
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Улучшенный старт с клавиатурой"""
keyboard = create_main_menu()
await update.message.reply_text(
    WELCOME_MESSAGE,
    parse_mode='Markdown',
    reply_markup=keyboard
)
async def sсhedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Красивое отображение расписания"""
    #Вы получаете данные
    lessons = db.get_all_lessons()
    message = format_sсhedule_message(lessons)
    await update.message.reply_text(message, parse_mode='Markdown')

async def delete_lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
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

        confirmation_text = f''
        'Подтверждение удаление'

        {format_lesson_message(lesson)}

        await update.message.reply_text(
            confirmation_text,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    except ValueError:
        await update.message.reply_text(format_error_message('time_format'))