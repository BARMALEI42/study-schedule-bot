from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


def create_main_menu(subgroup: str = '1') -> ReplyKeyboardMarkup:
    """Главное меню бота с указанием подгруппы"""
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
            KeyboardButton(f"🎯 Подгруппа {subgroup}"),
            KeyboardButton("❓ Помощь")
        ]
    ]
    return ReplyKeyboardMarkup(menu, resize_keyboard=True, one_time_keyboard=False)


def create_subgroup_selection_keyboard(current_subgroup: str = '1') -> InlineKeyboardMarkup:
    """Выбор подгруппы"""
    keyboard = [
        [
            InlineKeyboardButton(
                "🎯 Подгруппа 1" + (" ✅" if current_subgroup == '1' else ""),
                callback_data="subgroup_1"
            ),
            InlineKeyboardButton(
                "🎯 Подгруппа 2" + (" ✅" if current_subgroup == '2' else ""),
                callback_data="subgroup_2"
            )
        ],
        [
            InlineKeyboardButton(
                "👥 Для всех подгрупп" + (" ✅" if current_subgroup == 'all' else ""),
                callback_data="subgroup_all"
            )
        ],
        [
            InlineKeyboardButton("❌ Отмена", callback_data="cancel_subgroup")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_day_selection_keyboard(subgroup: str = '1') -> InlineKeyboardMarkup:
    """Inline-клавиатура для выбора дня недели с подгруппой"""
    keyboard = [
        [
            InlineKeyboardButton("Понедельник", callback_data=f"day_Понедельник_{subgroup}"),
            InlineKeyboardButton("Вторник", callback_data=f"day_Вторник_{subgroup}")
        ],
        [
            InlineKeyboardButton("Среда", callback_data=f"day_Среда_{subgroup}"),
            InlineKeyboardButton("Четверг", callback_data=f"day_Четверг_{subgroup}")
        ],
        [
            InlineKeyboardButton("Пятница", callback_data=f"day_Пятница_{subgroup}"),
            InlineKeyboardButton("Суббота", callback_data=f"day_Суббота_{subgroup}")
        ],
        [
            InlineKeyboardButton("Воскресенье", callback_data=f"day_Воскресенье_{subgroup}"),
            InlineKeyboardButton("📋 Вся неделя", callback_data=f"day_Вся неделя_{subgroup}")
        ],
        [
            InlineKeyboardButton(f"🎯 Подгруппа {subgroup}", callback_data="change_subgroup"),
            InlineKeyboardButton("❌ Отмена", callback_data="cancel")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_day_selection_compact(subgroup: str = '1') -> InlineKeyboardMarkup:
    """Компактная клавиатура для выбора дня с подгруппой"""
    keyboard = [
        [
            InlineKeyboardButton("Пн", callback_data=f"day_Понедельник_{subgroup}"),
            InlineKeyboardButton("Вт", callback_data=f"day_Вторник_{subgroup}"),
            InlineKeyboardButton("Ср", callback_data=f"day_Среда_{subgroup}"),
            InlineKeyboardButton("Чт", callback_data=f"day_Четверг_{subgroup}")
        ],
        [
            InlineKeyboardButton("Пт", callback_data=f"day_Пятница_{subgroup}"),
            InlineKeyboardButton("Сб", callback_data=f"day_Суббота_{subgroup}"),
            InlineKeyboardButton("Вс", callback_data=f"day_Воскресенье_{subgroup}"),
            InlineKeyboardButton("📋 Все", callback_data=f"day_Вся неделя_{subgroup}")
        ],
        [
            InlineKeyboardButton(f"🎯 Подгр. {subgroup}", callback_data="change_subgroup")
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


def create_add_lesson_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для добавления урока с выбором подгруппы"""
    keyboard = [
        [
            InlineKeyboardButton("Для подгруппы 1", callback_data="add_for_1"),
            InlineKeyboardButton("Для подгруппы 2", callback_data="add_for_2")
        ],
        [
            InlineKeyboardButton("Для всех подгрупп", callback_data="add_for_all"),
            InlineKeyboardButton("❌ Отмена", callback_data="cancel_add")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_clear_day_keyboard(subgroup: str = 'all') -> InlineKeyboardMarkup:
    """Клавиатура для очистки дня с подгруппой"""
    keyboard = [
        [
            InlineKeyboardButton("Понедельник", callback_data=f"clear_Понедельник_{subgroup}"),
            InlineKeyboardButton("Вторник", callback_data=f"clear_Вторник_{subgroup}"),
            InlineKeyboardButton("Среда", callback_data=f"clear_Среда_{subgroup}")
        ],
        [
            InlineKeyboardButton("Четверг", callback_data=f"clear_Четверг_{subgroup}"),
            InlineKeyboardButton("Пятница", callback_data=f"clear_Пятница_{subgroup}"),
            InlineKeyboardButton("Суббота", callback_data=f"clear_Суббота_{subgroup}")
        ],
        [
            InlineKeyboardButton("Воскресенье", callback_data=f"clear_Воскресенье_{subgroup}"),
            InlineKeyboardButton(f"🗑️ Все ({subgroup})", callback_data=f"clear_all_{subgroup}")
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


def create_week_navigation_keyboard(current_day: str = None, subgroup: str = '1') -> InlineKeyboardMarkup:
    """Навигация по дням недели с подгруппой"""
    days_order = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

    if current_day in days_order:
        current_index = days_order.index(current_day)
        prev_day = days_order[(current_index - 1) % 7]
        next_day = days_order[(current_index + 1) % 7]

        keyboard = [
            [
                InlineKeyboardButton(f"◀️ {prev_day}", callback_data=f"nav_{prev_day}_{subgroup}"),
                InlineKeyboardButton(f"{next_day} ▶️", callback_data=f"nav_{next_day}_{subgroup}")
            ],
            [
                InlineKeyboardButton("📋 Вся неделя", callback_data=f"nav_week_{subgroup}"),
                InlineKeyboardButton("🏠 В меню", callback_data="nav_menu")
            ]
        ]
    else:
        keyboard = [
            [
                InlineKeyboardButton("📅 Понедельник", callback_data=f"nav_Понедельник_{subgroup}"),
                InlineKeyboardButton("📅 Вторник", callback_data=f"nav_Вторник_{subgroup}"),
                InlineKeyboardButton("📅 Среда", callback_data=f"nav_Среда_{subgroup}")
            ],
            [
                InlineKeyboardButton("📅 Четверг", callback_data=f"nav_Четверг_{subgroup}"),
                InlineKeyboardButton("📅 Пятница", callback_data=f"nav_Пятница_{subgroup}"),
                InlineKeyboardButton("📅 Суббота", callback_data=f"nav_Суббота_{subgroup}")
            ],
            [
                InlineKeyboardButton("📅 Воскресенье", callback_data=f"nav_Воскресенье_{subgroup}"),
                InlineKeyboardButton("📋 Вся неделя", callback_data=f"nav_week_{subgroup}")
            ],
            [
                InlineKeyboardButton(f"🎯 Подгр. {subgroup}", callback_data="change_subgroup"),
                InlineKeyboardButton("🏠 В меню", callback_data="nav_menu")
            ]
        ]

    return InlineKeyboardMarkup(keyboard)


def create_schedule_actions_keyboard(day: str, subgroup: str = '1') -> InlineKeyboardMarkup:
    """Действия с расписанием на конкретный день"""
    keyboard = [
        [
            InlineKeyboardButton("➕ Добавить урок", callback_data=f"add_to_{day}_{subgroup}"),
            InlineKeyboardButton("🗑️ Очистить день", callback_data=f"clear_{day}_{subgroup}")
        ],
        [
            InlineKeyboardButton("◀️ Предыдущий день", callback_data=f"prev_{day}_{subgroup}"),
            InlineKeyboardButton("Следующий день ▶️", callback_data=f"next_{day}_{subgroup}")
        ],
        [
            InlineKeyboardButton("📋 Вся неделя", callback_data=f"show_week_{subgroup}"),
            InlineKeyboardButton("🎯 Сменить подгруппу", callback_data="change_subgroup"),
            InlineKeyboardButton("🏠 В меню", callback_data="go_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_quick_schedule_keyboard(subgroup: str = '1') -> ReplyKeyboardMarkup:
    """Быстрая клавиатура для просмотра расписания"""
    keyboard = [
        ["Понедельник", "Вторник", "Среда"],
        ["Четверг", "Пятница", "Суббота"],
        ["Воскресенье", "Вся неделя", "Сегодня"],
        [f"Подгруппа: {subgroup}"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


def create_stats_keyboard(subgroup: str = '1') -> InlineKeyboardMarkup:
    """Клавиатура для статистики с подгруппой"""
    keyboard = [
        [
            InlineKeyboardButton(f"📊 Общая ({subgroup})", callback_data=f"stats_general_{subgroup}"),
            InlineKeyboardButton(f"📅 По дням ({subgroup})", callback_data=f"stats_by_day_{subgroup}")
        ],
        [
            InlineKeyboardButton(f"📚 По предметам ({subgroup})", callback_data=f"stats_by_subject_{subgroup}"),
            InlineKeyboardButton(f"⏰ По времени ({subgroup})", callback_data=f"stats_by_time_{subgroup}")
        ],
        [
            InlineKeyboardButton(f"🔄 Обновить", callback_data=f"stats_refresh_{subgroup}"),
            InlineKeyboardButton("🎯 Сменить подгруппу", callback_data="change_subgroup"),
            InlineKeyboardButton("🏠 В меню", callback_data="stats_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_subgroup_filter_keyboard(current_subgroup: str = 'all') -> InlineKeyboardMarkup:
    """Клавиатура для фильтрации по подгруппам"""
    keyboard = [
        [
            InlineKeyboardButton(
                "🎯 Только 1" + (" ✅" if current_subgroup == '1' else ""),
                callback_data="filter_1"
            ),
            InlineKeyboardButton(
                "🎯 Только 2" + (" ✅" if current_subgroup == '2' else ""),
                callback_data="filter_2"
            )
        ],
        [
            InlineKeyboardButton(
                "👥 Все подгруппы" + (" ✅" if current_subgroup == 'all' else ""),
                callback_data="filter_all"
            ),
            InlineKeyboardButton(
                "👥 Для всех" + (" ✅" if current_subgroup == 'common' else ""),
                callback_data="filter_common"
            )
        ],
        [
            InlineKeyboardButton("❌ Сбросить фильтр", callback_data="filter_reset"),
            InlineKeyboardButton("❌ Отмена", callback_data="cancel_filter")
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


def create_subgroup_switch_keyboard(current_subgroup: str) -> InlineKeyboardMarkup:
    """Быстрое переключение подгруппы"""
    keyboard = [
        [
            InlineKeyboardButton("🎯 1", callback_data="switch_1"),
            InlineKeyboardButton("🎯 2", callback_data="switch_2"),
            InlineKeyboardButton("👥 Все", callback_data="switch_all")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# ===== СТАРЫЕ ФУНКЦИИ ДЛЯ СОВМЕСТИМОСТИ =====

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


# ===== НОВЫЕ ФУНКЦИИ ДЛЯ ПОДГРУПП =====

def create_subgroup_management_keyboard() -> InlineKeyboardMarkup:
    """Управление подгруппами"""
    keyboard = [
        [
            InlineKeyboardButton("🎯 Выбрать подгруппу", callback_data="manage_select"),
            InlineKeyboardButton("👥 Показать все", callback_data="manage_show_all")
        ],
        [
            InlineKeyboardButton("➕ Добавить для подгр. 1", callback_data="manage_add_1"),
            InlineKeyboardButton("➕ Добавить для подгр. 2", callback_data="manage_add_2")
        ],
        [
            InlineKeyboardButton("📊 Статистика по подгруппам", callback_data="manage_stats"),
            InlineKeyboardButton("🏠 В меню", callback_data="manage_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_lesson_detail_keyboard(lesson_id: int, subgroup: str = 'all') -> InlineKeyboardMarkup:
    """Детали урока с подгруппой"""
    keyboard = [
        [
            InlineKeyboardButton("✏️ Изменить", callback_data=f"edit_{lesson_id}"),
            InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_{lesson_id}")
        ],
        [
            InlineKeyboardButton(f"🎯 Подгр. {subgroup}", callback_data=f"subgroup_{subgroup}"),
            InlineKeyboardButton("↩️ Назад", callback_data="back_to_list")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)