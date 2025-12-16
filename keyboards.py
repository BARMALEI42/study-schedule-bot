from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

# === КОНСТАНТЫ ===
DAYS_FULL = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]


# === ОСНОВНЫЕ КЛАВИАТУРЫ ===
def create_main_menu(subgroup: str = '1') -> ReplyKeyboardMarkup:
    """Главное меню бота"""
    menu = [
        ["📅 Сегодня", "📅 Завтра"],
        ["📋 Вся неделя", "➕ Добавить урок"],
        ["🗑️ Удалить урок", "📊 Статистика"],
        [f"🎯 Подгруппа {subgroup}", "❓ Помощь"]
    ]
    return ReplyKeyboardMarkup(menu, resize_keyboard=True, one_time_keyboard=False)


def create_subgroup_selection_keyboard(current_subgroup: str = '1') -> InlineKeyboardMarkup:
    """Выбор подгруппы"""

    def _subgroup_button(subgroup: str, text: str) -> InlineKeyboardButton:
        if subgroup == current_subgroup:
            text += " ✅"
        return InlineKeyboardButton(text, callback_data=f"subgroup_{subgroup}")

    keyboard = [
        [_subgroup_button('1', "🎯 Подгруппа 1"), _subgroup_button('2', "🎯 Подгруппа 2")],
        [_subgroup_button('all', "👥 Для всех")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_day_selection_keyboard(subgroup: str = '1') -> InlineKeyboardMarkup:
    """Клавиатура для выбора дня недели"""

    def _day_button(day: str) -> InlineKeyboardButton:
        return InlineKeyboardButton(day, callback_data=f"day_{day}_{subgroup}")

    # 7 дней недели + "Вся неделя"
    keyboard = [
        [_day_button(DAYS_FULL[0]), _day_button(DAYS_FULL[1]), _day_button(DAYS_FULL[2])],
        [_day_button(DAYS_FULL[3]), _day_button(DAYS_FULL[4]), _day_button(DAYS_FULL[5])],
        [_day_button(DAYS_FULL[6]), InlineKeyboardButton("📋 Вся неделя", callback_data=f"day_Вся неделя_{subgroup}")]
    ]

    # Нижний ряд
    keyboard.append([
        InlineKeyboardButton(f"🎯 Подгр. {subgroup}", callback_data="change_subgroup"),
        InlineKeyboardButton("❌ Отмена", callback_data="cancel")
    ])

    return InlineKeyboardMarkup(keyboard)


def create_confirmation_keyboard(lesson_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения удаления"""
    keyboard = [[
        InlineKeyboardButton("✅ Да, удалить", callback_data=f"confirm_delete_{lesson_id}"),
        InlineKeyboardButton("❌ Нет, оставить", callback_data="cancel_delete")
    ]]
    return InlineKeyboardMarkup(keyboard)