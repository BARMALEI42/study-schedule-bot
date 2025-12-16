from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

# === КОНСТАНТЫ ===
DAYS_FULL = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
DAYS_SHORT = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
TIME_SLOTS = ["8:00", "9:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00",
              "20:00", "21:00"]


# === УТИЛИТНЫЕ ФУНКЦИИ ===
def _day_button(day: str, subgroup: str, short: bool = False) -> InlineKeyboardButton:
    """Создать кнопку дня"""
    day_text = day[:2] if short and len(day) > 2 else day
    return InlineKeyboardButton(day_text, callback_data=f"day_{day}_{subgroup}")


def _subgroup_button(subgroup: str, current_subgroup: str) -> InlineKeyboardButton:
    """Создать кнопку подгруппы с отметкой выбора"""
    texts = {
        '1': "🎯 Подгруппа 1",
        '2': "🎯 Подгруппа 2",
        'all': "👥 Для всех подгрупп",
        'common': "👥 Для всех"
    }
    text = texts.get(subgroup, f"Подгр. {subgroup}")
    if subgroup == current_subgroup:
        text += " ✅"
    return InlineKeyboardButton(text, callback_data=f"subgroup_{subgroup}")


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
    keyboard = [
        [_subgroup_button('1', current_subgroup), _subgroup_button('2', current_subgroup)],
        [_subgroup_button('all', current_subgroup)],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_subgroup")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_day_selection_keyboard(subgroup: str = '1', compact: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура для выбора дня недели"""
    if compact:
        # Компактный вариант с короткими названиями дней
        keyboard = [
            [_day_button(day, subgroup, short=True) for day in DAYS_FULL[:4]],
            [_day_button(day, subgroup, short=True) for day in DAYS_FULL[4:]] +
            [InlineKeyboardButton("📋 Все", callback_data=f"day_Вся неделя_{subgroup}")]
        ]
    else:
        # Полный вариант
        keyboard = [
            [_day_button(DAYS_FULL[0], subgroup), _day_button(DAYS_FULL[1], subgroup)],
            [_day_button(DAYS_FULL[2], subgroup), _day_button(DAYS_FULL[3], subgroup)],
            [_day_button(DAYS_FULL[4], subgroup), _day_button(DAYS_FULL[5], subgroup)],
            [_day_button(DAYS_FULL[6], subgroup),
             InlineKeyboardButton("📋 Вся неделя", callback_data=f"day_Вся неделя_{subgroup}")]
        ]

    # Добавляем нижний ряд
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


def create_time_slots_keyboard() -> InlineKeyboardMarkup:
    """Выбор временных слотов"""
    keyboard = []
    for i in range(0, len(TIME_SLOTS), 4):  # По 4 кнопки в ряд
        row = []
        for time in TIME_SLOTS[i:i + 4]:
            row.append(InlineKeyboardButton(time, callback_data=f"time_{time}"))
        keyboard.append(row)

    # Добавляем дополнительные кнопки
    keyboard.append([
        InlineKeyboardButton("Другое время", callback_data="custom_time"),
        InlineKeyboardButton("❌ Отмена", callback_data="cancel_time")
    ])

    return InlineKeyboardMarkup(keyboard)


def create_week_navigation_keyboard(current_day: str = None, subgroup: str = '1') -> InlineKeyboardMarkup:
    """Навигация по дням недели"""
    if current_day and current_day in DAYS_FULL:
        # Навигация вперед/назад если выбран день
        current_idx = DAYS_FULL.index(current_day)
        prev_day = DAYS_FULL[(current_idx - 1) % 7]
        next_day = DAYS_FULL[(current_idx + 1) % 7]

        keyboard = [[
            InlineKeyboardButton(f"◀️ {prev_day}", callback_data=f"nav_{prev_day}_{subgroup}"),
            InlineKeyboardButton(f"{next_day} ▶️", callback_data=f"nav_{next_day}_{subgroup}")
        ]]
    else:
        # Показать все дни если день не выбран
        keyboard = []
        for i in range(0, 7, 3):  # По 3 дня в ряд
            row = []
            for day in DAYS_FULL[i:i + 3]:
                row.append(InlineKeyboardButton(f"📅 {day}", callback_data=f"nav_{day}_{subgroup}"))
            keyboard.append(row)

    # Общие кнопки
    keyboard.append([
        InlineKeyboardButton("📋 Вся неделя", callback_data=f"nav_week_{subgroup}"),
        InlineKeyboardButton(f"🎯 Подгр. {subgroup}", callback_data="change_subgroup"),
        InlineKeyboardButton("🏠 В меню", callback_data="nav_menu")
    ])

    return InlineKeyboardMarkup(keyboard)


def create_schedule_actions_keyboard(day: str, subgroup: str = '1') -> InlineKeyboardMarkup:
    """Действия с расписанием на конкретный день"""
    keyboard = [
        [
            InlineKeyboardButton("➕ Добавить урок", callback_data=f"add_to_{day}_{subgroup}"),
            InlineKeyboardButton("🗑️ Очистить день", callback_data=f"clear_{day}_{subgroup}")
        ],
        [
            InlineKeyboardButton("◀️ Пред. день", callback_data=f"prev_{day}_{subgroup}"),
            InlineKeyboardButton("След. день ▶️", callback_data=f"next_{day}_{subgroup}")
        ],
        [
            InlineKeyboardButton("📋 Вся неделя", callback_data=f"show_week_{subgroup}"),
            InlineKeyboardButton("🎯 Подгр.", callback_data="change_subgroup"),
            InlineKeyboardButton("🏠 В меню", callback_data="go_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# === СПЕЦИАЛЬНЫЕ КЛАВИАТУРЫ ===
def create_stats_keyboard(subgroup: str = '1') -> InlineKeyboardMarkup:
    """Клавиатура для статистики"""
    keyboard = [
        [
            InlineKeyboardButton(f"📊 Общая", callback_data=f"stats_general_{subgroup}"),
            InlineKeyboardButton(f"📅 По дням", callback_data=f"stats_by_day_{subgroup}")
        ],
        [
            InlineKeyboardButton(f"📚 По предметам", callback_data=f"stats_by_subject_{subgroup}"),
            InlineKeyboardButton(f"🔄 Обновить", callback_data=f"stats_refresh_{subgroup}")
        ],
        [
            InlineKeyboardButton("🎯 Подгр.", callback_data="change_subgroup"),
            InlineKeyboardButton("🏠 В меню", callback_data="stats_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_quick_schedule_keyboard(subgroup: str = '1') -> ReplyKeyboardMarkup:
    """Быстрая клавиатура для просмотра расписания"""
    keyboard = [
        DAYS_FULL[:3],
        DAYS_FULL[3:6],
        [DAYS_FULL[6], "Вся неделя", "Сегодня"],
        [f"Подгруппа: {subgroup}"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)


def create_subgroup_filter_keyboard(current_subgroup: str = 'all') -> InlineKeyboardMarkup:
    """Фильтрация по подгруппам"""
    keyboard = [
        [_subgroup_button('1', current_subgroup), _subgroup_button('2', current_subgroup)],
        [_subgroup_button('all', current_subgroup), _subgroup_button('common', current_subgroup)],
        [
            InlineKeyboardButton("❌ Сбросить", callback_data="filter_reset"),
            InlineKeyboardButton("❌ Отмена", callback_data="cancel_filter")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_subgroup_management_keyboard() -> InlineKeyboardMarkup:
    """Управление подгруппами"""
    keyboard = [
        [
            InlineKeyboardButton("🎯 Выбрать", callback_data="manage_select"),
            InlineKeyboardButton("👥 Показать все", callback_data="manage_show_all")
        ],
        [
            InlineKeyboardButton("➕ Для подгр. 1", callback_data="manage_add_1"),
            InlineKeyboardButton("➕ Для подгр. 2", callback_data="manage_add_2")
        ],
        [
            InlineKeyboardButton("📊 Статистика", callback_data="manage_stats"),
            InlineKeyboardButton("🏠 В меню", callback_data="manage_menu")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_lesson_detail_keyboard(lesson_id: int, subgroup: str = 'all') -> InlineKeyboardMarkup:
    """Детали урока"""
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


# === УНИВЕРСАЛЬНЫЕ КЛАВИАТУРЫ ===
def create_yes_no_keyboard(yes_text: str = "✅ Да", yes_data: str = "yes",
                           no_text: str = "❌ Нет", no_data: str = "no") -> InlineKeyboardMarkup:
    """Универсальная клавиатура Да/Нет"""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton(yes_text, callback_data=yes_data),
        InlineKeyboardButton(no_text, callback_data=no_data)
    ]])


def create_cancel_keyboard(cancel_text: str = "❌ Отмена",
                           cancel_data: str = "cancel") -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    return InlineKeyboardMarkup([[InlineKeyboardButton(cancel_text, callback_data=cancel_data)]])


def create_back_keyboard(back_text: str = "↩️ Назад",
                         back_data: str = "back") -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой 'Назад'"""
    return InlineKeyboardMarkup([[InlineKeyboardButton(back_text, callback_data=back_data)]])


def create_home_keyboard(home_text: str = "🏠 В меню",
                         home_data: str = "home") -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой 'В меню'"""
    return InlineKeyboardMarkup([[InlineKeyboardButton(home_text, callback_data=home_data)]])


def create_subgroup_switch_keyboard(current_subgroup: str) -> InlineKeyboardMarkup:
    """Быстрое переключение подгруппы"""
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🎯 1", callback_data="switch_1"),
        InlineKeyboardButton("🎯 2", callback_data="switch_2"),
        InlineKeyboardButton("👥 Все", callback_data="switch_all")
    ]])


# === ОЧИСТКА ДНЯ (специальная клавиатура) ===
def create_clear_day_keyboard(subgroup: str = 'all') -> InlineKeyboardMarkup:
    """Очистка дня"""
    keyboard = []
    for i in range(0, 7, 3):  # По 3 дня в ряд
        row = []
        for day in DAYS_FULL[i:i + 3]:
            row.append(InlineKeyboardButton(day, callback_data=f"clear_{day}_{subgroup}"))
        keyboard.append(row)

    keyboard.append([
        InlineKeyboardButton(f"🗑️ Все ({subgroup})", callback_data=f"clear_all_{subgroup}"),
        InlineKeyboardButton("❌ Отмена", callback_data="cancel_clear")
    ])

    return InlineKeyboardMarkup(keyboard)