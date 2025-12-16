from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

# === КОНСТАНТЫ ===
DAYS_FULL = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]


# === ОСНОВНЫЕ КЛАВИАТУРЫ ===
def create_main_menu(subgroup: str = '1') -> ReplyKeyboardMarkup:
    """Главное меню бота - ОБЫЧНАЯ КЛАВИАТУРА"""
    menu = [
        ["📅 Сегодня", "📅 Завтра"],
        ["📋 Вся неделя", "➕ Добавить урок"],
        ["🗑️ Удалить урок", "📊 Статистика"],
        [f"🎯 Подгруппа {subgroup}", "❓ Помощь"]
    ]
    return ReplyKeyboardMarkup(menu, resize_keyboard=True, one_time_keyboard=False)


def create_subgroup_selection_keyboard(current_subgroup: str = '1') -> InlineKeyboardMarkup:
    """Выбор подгруппы - INLINE КЛАВИАТУРА"""
    keyboard = [
        [
            InlineKeyboardButton("🎯 Подгруппа 1" + (" ✅" if current_subgroup == '1' else ""),
                                 callback_data="subgroup_1"),
            InlineKeyboardButton("🎯 Подгруппа 2" + (" ✅" if current_subgroup == '2' else ""),
                                 callback_data="subgroup_2")
        ],
        [InlineKeyboardButton("👥 Для всех" + (" ✅" if current_subgroup == 'all' else ""),
                              callback_data="subgroup_all")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_day_selection_keyboard(subgroup: str = '1') -> InlineKeyboardMarkup:
    """Клавиатура для выбора дня недели - INLINE КЛАВИАТУРА"""
    # Создаем кнопки дней
    keyboard = []
    for i in range(0, len(DAYS_FULL), 3):
        row = []
        for day in DAYS_FULL[i:i + 3]:
            row.append(InlineKeyboardButton(day, callback_data=f"day_{day}_{subgroup}"))
        keyboard.append(row)

    # Добавляем кнопку "Вся неделя" и отмены
    keyboard.append([
        InlineKeyboardButton("📋 Вся неделя", callback_data=f"day_Вся неделя_{subgroup}"),
        InlineKeyboardButton("❌ Отмена", callback_data="cancel")
    ])

    return InlineKeyboardMarkup(keyboard)


def create_confirmation_keyboard(lesson_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения удаления - INLINE КЛАВИАТУРА"""
    keyboard = [[
        InlineKeyboardButton("✅ Да, удалить", callback_data=f"confirm_delete_{lesson_id}"),
        InlineKeyboardButton("❌ Нет, оставить", callback_data="cancel_delete")
    ]]
    return InlineKeyboardMarkup(keyboard)