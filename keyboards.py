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
    """Клавиатура подтверждения удаления"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Да, удалить", callback_data=f"confirm_delete_{lesson_id}"),
            InlineKeyboardButton("❌ Отменить", callback_data="cancel_delete")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_day_selection_keyboard() -> InlineKeyboardMarkup:
    """Выбор дня недели"""
    keyboard = [
        [InlineKeyboardButton("Понедельник", callback_data="day_monday")],
        [InlineKeyboardButton("Вторник", callback_data="day_tuesday")],
        [InlineKeyboardButton("Среда", callback_data="day_wednesday")],
        [InlineKeyboardButton("Четверг", callback_data="day_thursday")],
        [InlineKeyboardButton("Пятница", callback_data="day_friday")],
        [InlineKeyboardButton("Суббота", callback_data="day_saturday")],
        [InlineKeyboardButton("Воскресенье", callback_data="day_sunday")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_add")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_time_selection_keyboard() -> InlineKeyboardMarkup:
    """Выбор времени (основные интервалы)"""
    keyboard = []

    # Утренние пары
    morning_times = ["8:00", "9:00", "10:00", "11:00"]
    morning_row = []
    for time in morning_times:
        morning_row.append(InlineKeyboardButton(time, callback_data=f"time_{time}"))
    keyboard.append(morning_row)

    # Дневные пары
    afternoon_times = ["12:00", "13:00", "14:00", "15:00"]
    afternoon_row = []
    for time in afternoon_times:
        afternoon_row.append(InlineKeyboardButton(time, callback_data=f"time_{time}"))
    keyboard.append(afternoon_row)

    # Вечерние пары
    evening_times = ["16:00", "17:00", "18:00", "19:00"]
    evening_row = []
    for time in evening_times:
        evening_row.append(InlineKeyboardButton(time, callback_data=f"time_{time}"))
    keyboard.append(evening_row)

    # Кнопка отмены
    keyboard.append([InlineKeyboardButton("❌ Отмена", callback_data="cancel_add")])

    return InlineKeyboardMarkup(keyboard)


def create_settings_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура настроек"""
    keyboard = [
        [InlineKeyboardButton("⏰ Настройка уведомлений", callback_data="settings_notifications")],
        [InlineKeyboardButton("🎨 Изменить тему", callback_data="settings_theme")],
        [InlineKeyboardButton("🗑️ Очистить расписание", callback_data="settings_clear")],
        [InlineKeyboardButton("↩️ Назад в меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_cancel_keyboard() -> InlineKeyboardMarkup:
    """Простая клавиатура для отмены действия"""
    keyboard = [
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_action")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_back_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой "Назад" """
    keyboard = [
        [InlineKeyboardButton("↩️ Назад", callback_data="go_back")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_yes_no_keyboard(yes_data="yes", no_data="no") -> InlineKeyboardMarkup:
    """Универсальная клавиатура Да/Нет"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Да", callback_data=yes_data),
            InlineKeyboardButton("❌ Нет", callback_data=no_data)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)