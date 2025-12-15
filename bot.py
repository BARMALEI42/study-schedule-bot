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