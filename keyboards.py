from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


def create_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню бота (Reply-клавиатура для быстрого доступа)"""
    menu = [
        [
            KeyboardButton("📅 Сегодня"),
            KeyboardButton("📅 Завтра")
        ],
        [
            KeyboardButton("📋 Вся неделя"),
            KeyboardButton("➕ Добавить урок")
        ],
        [
            KeyboardButton("🗑️ Удалить урок"),
            KeyboardButton("📊 Статистика")
        ],
        [
            KeyboardButton("❓ Помощь")
        ]
    ]
    return ReplyKeyboardMarkup(menu, resize_keyboard=True, one_time_keyboard=False)


def create_day_selection_keyboard() -> InlineKeyboardMarkup:
    """Inline-клавиатура для выбора дня недели"""
    keyboard = [
        [
            InlineKeyboardButton("Понедельник", callback_data="day_Понедельник"),
            InlineKeyboardButton("Вторник", callback_data="day_Вторник")
        ],
        [
            InlineKeyboardButton("Среда", callback_data="day_Среда"),
            InlineKeyboardButton("Четверг", callback_data="day_Четверг")
        ],
        [
            InlineKeyboardButton("Пятница", callback_data="day_Пятница"),
            InlineKeyboardButton("Суббота", callback_data="day_Суббота")
        ],
        [
            InlineKeyboardButton("Воскресенье", callback_data="day_Воскресенье"),
            InlineKeyboardButton("📋 Вся неделя", callback_data="day_Вся неделя")
        ],
        [
            InlineKeyboardButton("❌ Отмена", callback_data="cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_day_selection_compact() -> InlineKeyboardMarkup:
    """Компактная клавиатура для выбора дня"""
    keyboard = [
        [
            InlineKeyboardButton("Пн", callback_data="day_Понедельник"),
            InlineKeyboardButton("Вт", callback_data="day_Вторник"),
            InlineKeyboardButton("Ср", callback_data="day_Среда"),
            InlineKeyboardButton("Чт", callback_data="day_Четверг")
        ],
        [
            InlineKeyboardButton("Пт", callback_data="day_Пятница"),
            InlineKeyboardButton("Сб", callback_data="day_Суббота"),
            InlineKeyboardButton("Вс", callback_data="day_Воскресенье"),
            InlineKeyboardButton("📋 Все", callback_data="day_Вся неделя")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_confirmation_keyboard(lesson_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения удаления"""
    keyboard = [
        [
            InlineKeyboardButton("✅ Да, удалить", callback_data=f"confirm_delete_{lesson_id}"),
            InlineKeyboardButton("❌ Нет, оставить", callback_data="cancel_delete")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_clear_day_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для очистки дня"""
    keyboard = [
        [
            InlineKeyboardButton("Понедельник", callback_data="clear_Понедельник"),
            InlineKeyboardButton("Вторник", callback_data="clear_Вторник"),
            InlineKeyboardButton("Среда", callback_data="clear_Среда")
        ],
        [
            InlineKeyboardButton("Четверг", callback_data="clear_Четверг"),
            InlineKeyboardButton("Пятница", callback_data="clear_Пятница"),
            InlineKeyboardButton("Суббота", callback_data="clear_Суббота")
        ],
        [
            InlineKeyboardButton("Воскресенье", callback_data="clear_Воскресенье"),
            InlineKeyboardButton("🗑️ Все дни", callback_data="clear_all")
        ],
        [
            InlineKeyboardButton("❌ Отмена", callback_data="cancel_clear")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_time_slots_keyboard() -> InlineKeyboardMarkup:
    """Выбор временных слотов"""
    time_slots = [
        ["8:00", "9:00", "10:00", "11:00"],
        ["12:00", "13:00", "14:00", "15:00"],
        ["16:00", "17:00", "18:00", "19:00"],
        ["20:00", "21:00", "Другое время", "❌ Отмена"]
    ]

    keyboard = []
    for row in time_slots:
        keyboard_row = []
        for time in row:
            if time == "Другое время":
                keyboard_row.append(InlineKeyboardButton(time, callback_data="custom_time"))
            elif time == "❌ Отмена":
                keyboard_row.append(InlineKeyboardButton(time, callback_data="cancel_time"))
            else:
                keyboard_row.append(InlineKeyboardButton(time, callback_data=f"time_{time}"))
        keyboard.append(keyboard_row)

    return InlineKeyboardMarkup(keyboard)


def create_week_navigation_keyboard(current_day: str = None) -> InlineKeyboardMarkup:
    """Навигация по дням недели (для просмотра расписания)"""
    days_order = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

    if current_day in days_order:
        current_index = days_order.index(current_day)
        prev_day = days_order[(current_index - 1) % 7]
        next_day = days_order[(current_index + 1) % 7]

        keyboard = [
            [
                InlineKeyboardButton(f"◀️ {prev_day}", callback_data=f"nav_{prev_day}"),
                InlineKeyboardButton(f"{next_day} ▶️", callback_data=f"nav_{next_day}")
            ],
            [
                InlineKeyboardButton("📋 Вся неделя", callback_data="nav_week"),
                InlineKeyboardButton("🏠 В меню", callback_data="nav_menu")
            ]
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton("📅 Понедельник", callback_data="nav_Понедельник"),
                InlineKeyboardButton("📅 Вторник", callback_data="nav_Вторник"),
                InlineKeyboardButton("📅 Среда", callback_data="nav_Среда")
            ],
            [
                InlineKeyboardButton("📅 Четверг", callback_data="nav_Четверг"),
                InlineKeyboardButton("📅 Пятница", callback_data="nav_Пятница"),
                InlineKeyboardButton("📅 Суббота", callback_data="nav_Суббота")
            ],
            [
                InlineKeyboardButton("📅 Воскресенье", callback_data="nav_Воскресенье"),
                InlineKeyboardButton("📋 Вся неделя", callback_data="nav_week")
            ],
            [
                InlineKeyboardButton("🏠 В меню", callback_data="nav_menu")
            ]
        ]

    return InlineKeyboardMarkup(keyboard)


def create_schedule_actions_keyboard(day: str) -> InlineKeyboardMarkup:
    """Действия с расписанием на конкретный день"""
    keyboard = [
        [
            InlineKeyboardButton("➕ Добавить урок", callback_data=f"add_to_{day}"),
            InlineKeyboardButton("🗑️ Очистить день", callback_data=f"clear_{day}")
        ],
        [
            InlineKeyboardButton("◀️ Предыдущий день", callback_data=f"prev_{day}"),
            InlineKeyboardButton("Следующий день ▶️", callback_data=f"next_{day}")
        ],
        [
            InlineKeyboardButton("📋 Вся неделя", callback_data="show_week"),
            InlineKeyboardButton("🏠 В меню", callback_data="go_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_quick_schedule_keyboard() -> ReplyKeyboardMarkup:
    """Быстрая клавиатура для просмотра расписания"""
    keyboard = [
        ["Понедельник", "Вторник", "Среда"],
        ["Четверг", "Пятница", "Суббота"],
        ["Воскресенье", "Вся неделя", "Сегодня"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


def create_stats_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для статистики"""
    keyboard = [
        [
            InlineKeyboardButton("📊 Общая статистика", callback_data="stats_general"),
            InlineKeyboardButton("📅 По дням", callback_data="stats_by_day")
        ],
        [
            InlineKeyboardButton("📚 По предметам", callback_data="stats_by_subject"),
            InlineKeyboardButton("⏰ По времени", callback_data="stats_by_time")
        ],
        [
            InlineKeyboardButton("🔄 Обновить", callback_data="stats_refresh"),
            InlineKeyboardButton("🏠 В меню", callback_data="stats_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_yes_no_keyboard(yes_text="✅ Да", yes_data="yes",
                           no_text="❌ Нет", no_data="no") -> InlineKeyboardMarkup:
    """Универсальная клавиатура Да/Нет"""
    keyboard = [
        [
            InlineKeyboardButton(yes_text, callback_data=yes_data),
            InlineKeyboardButton(no_text, callback_data=no_data)
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_cancel_keyboard(cancel_text="❌ Отмена", cancel_data="cancel") -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    keyboard = [
        [InlineKeyboardButton(cancel_text, callback_data=cancel_data)]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_back_keyboard(back_text="↩️ Назад", back_data="back") -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой "Назад" """
    keyboard = [
        [InlineKeyboardButton(back_text, callback_data=back_data)]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_home_keyboard(home_text="🏠 В меню", home_data="home") -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой "В меню" """
    keyboard = [
        [InlineKeyboardButton(home_text, callback_data=home_data)]
    ]
    return InlineKeyboardMarkup(keyboard)


# Устаревшие функции (можно удалить или оставить для совместимости)
def create_settings_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура настроек (устаревшая)"""
    keyboard = [
        [
            InlineKeyboardButton("↩️ В меню", callback_data="back_to_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_time_selection_keyboard() -> InlineKeyboardMarkup:
    """Выбор времени (устаревшая версия)"""
    return create_time_slots_keyboard()