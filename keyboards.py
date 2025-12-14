from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def create_main_menu() -> InlineKeyboardMarkup:
    """Создает главное меню с кнопками"""
    keyboard = [
[
    InlineKeyboardButton("📅 Расписание", callback_data="show_schedule"),
    InlineKeyboardButton("➕ Добавить", callback_data="add_lesson")
],
[
    InlineKeyboardButton("🗑️ Удалить", callback_data="delete_lesson"),
    InlineKeyboardButton("⚙️ Настройки", callback_data="settings")
],
[
    InlineKeyboardButton("🆘 Помощь", callback_data="help"),
    InlineKeyboardButton("📊 Статистика", callback_data="stats")
]
    ]
    return InlineKeyboardMarkup(keyboard)
def create_confirmation_keyboard(lesson_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждение удаления"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Да, удалить", callback_data=f"confirm_delete_{lesson_id}"),
            InlineKeyboardButton("❌ Отменить", callback_data="cancel_delete")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
def create_day_selection_keyboard() -> InlineKeyboardMarkup:
    """Выбор дни недели"""
    keyboard = [
        [InlineKeyboardButton("Понедельник", callback_data="day_monday")],
        [InlineKeyboardButton("Вторник", callback_data="day_tuesday")],
        [InlineKeyboardButton("Среда", callback_data="day_wednesday")],
        [InlineKeyboardButton("Четверг", callback_data="day_thursday")],
        [InlineKeyboardButton("Пятница", callback_data="day_friday")],
        [InlineKeyboardButton("Выходные", callback_data="day_weekend")],
    ]
    return InlineKeyboardMarkup(keyboard)