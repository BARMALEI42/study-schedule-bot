# === КОНСТАНТЫ ===
DAYS_FULL = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
DAYS_SHORT = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

DAY_EMOJIS = {
    'Понедельник': '📅', 'Вторник': '📅', 'Среда': '📅', 'Четверг': '📅',
    'Пятница': '📅', 'Суббота': '🎉', 'Воскресенье': '🌟'
}

DAY_NUMBER_EMOJIS = {
    'Понедельник': '1️⃣', 'Вторник': '2️⃣', 'Среда': '3️⃣', 'Четверг': '4️⃣',
    'Пятница': '5️⃣', 'Суббота': '6️⃣', 'Воскресенье': '7️⃣'
}

SUBGROUP_TEXTS = {
    '1': "🎯 (подгруппа 1)",
    '2': "🎯 (подгруппа 2)",
    'all': "👥 (для всех подгрупп)",
    'common': "👥 (для всех)"
}

# === ОСНОВНЫЕ СООБЩЕНИЯ ===
WELCOME_MESSAGE = """
👋 Добро пожаловать в бот-расписание с поддержкой подгрупп!

🎯 *Особенности:*
• Поддержка 2 подгрупп + общие уроки
• Индивидуальное расписание для каждой подгруппы
• Гибкое переключение между подгруппами
• Фильтрация уроков по подгруппам

📌 *Начните с выбора подгруппы:* /subgroup
"""

HELP_MESSAGE = """
🆘 *Справка по командам с поддержкой подгрупп*

🎯 *Работа с подгруппами:*
/subgroup - Выбрать подгруппу (1, 2 или all)
🔄 Подгруппа сохраняется для каждого пользователя отдельно

📅 *Просмотр расписания (для выбранной подгруппы):*
/schedule - Выбрать день недели
/today - Расписание на сегодня
/tomorrow - Расписание на завтра  
/week - Вся неделя
/stats - Статистика по подгруппе

➕ *Добавление урока (с указанием подгруппы):*
`/add <предмет> <время> <день> [подгруппа]`

*Примеры:*
• `/add Математика 10:00 Понедельник` - для всех
• `/add Математика 10:00 Понедельник 1` - для подгруппы 1
• `/add Математика 10:00 Понедельник 2` - для подгруппы 2
• `/add Математика 10:00 Понедельник all` - для всех подгрупп

🗑️ *Удаление:*
/delete <ID_урока> - Удалить урок
/clear <день> - Очистить весь день

📊 *Аналитика:*
/stats - Статистика для текущей подгруппы

💡 *Советы:*
• Используйте кнопки для быстрого доступа
• ID урока можно увидеть в расписании
• Подгруппа: 1, 2 или all (для всех)
• Дни: Понедельник-Воскресенье
"""


# === УТИЛИТНЫЕ ФУНКЦИИ ===
def _get_subgroup_mark(subgroup: str) -> str:
    """Получить маркер подгруппы"""
    if subgroup == '1':
        return " [1]"
    elif subgroup == '2':
        return " [2]"
    return ""


def _format_lessons_by_subgroup(lessons: list) -> dict:
    """Группировать уроки по подгруппам"""
    grouped = {'1': [], '2': [], 'all': []}
    for lesson in lessons:
        subgroup = lesson.get('subgroup', 'all')
        if subgroup in grouped:
            grouped[subgroup].append(lesson)
        else:
            grouped['all'].append(lesson)
    return grouped


def _format_subgroup_stats(grouped_lessons: dict) -> tuple:
    """Форматировать статистику по подгруппам"""
    counts = []
    stats = []

    if grouped_lessons['all']:
        counts.append(f"всех: {len(grouped_lessons['all'])}")
        stats.append(f"👥 всех: {len(grouped_lessons['all'])}")
    if grouped_lessons['1']:
        counts.append(f"подгр.1: {len(grouped_lessons['1'])}")
        stats.append(f"🎯 1: {len(grouped_lessons['1'])}")
    if grouped_lessons['2']:
        counts.append(f"подгр.2: {len(grouped_lessons['2'])}")
        stats.append(f"🎯 2: {len(grouped_lessons['2'])}")

    return counts, stats


# === ФОРМАТИРОВАНИЕ УРОКОВ ===
def format_lesson_message(lesson: dict) -> str:
    """Форматировать информацию об уроке"""
    subject = lesson.get('subject', 'Без названия')
    time = lesson.get('time', '--:--')
    day = lesson.get('day', 'Не указан')
    subgroup = lesson.get('subgroup', 'all')
    lesson_id = lesson.get('id', '?')

    subgroup_text = {
        '1': "🎯 Подгруппа: 1",
        '2': "🎯 Подгруппа: 2",
        'all': "👥 Для всех подгрупп"
    }.get(subgroup, f"Подгруппа: {subgroup}")

    return f"""📚 *{subject}*
🕗 Время: {time}
📆 День: {day}
{subgroup_text}
🆔 ID: {lesson_id}"""


def format_lesson_short(lesson: dict) -> str:
    """Краткая информация об уроке"""
    time_str = lesson.get('time', '--:--')
    subject_str = lesson.get('subject', 'Без названия')
    return f"• {time_str} - {subject_str}{_get_subgroup_mark(lesson.get('subgroup', 'all'))}"


# === ФОРМАТИРОВАНИЕ РАСПИСАНИЯ ===
def format_day_schedule(day: str, lessons: list) -> str:
    """Форматировать расписание для дня"""
    if not lessons:
        return f"📅 *{day}*\n\n🎉 На этот день нет запланированных уроков!"

    emoji = DAY_EMOJIS.get(day, '📅')
    grouped = _format_lessons_by_subgroup(lessons)

    message = f"{emoji} *{day}*\n\n"
    total_lessons = 0

    # Уроки для всех подгрупп
    if grouped['all']:
        message += "👥 *Для всех подгрупп:*\n"
        for i, lesson in enumerate(grouped['all'], 1):
            message += f"  {i}. {lesson.get('time')} - {lesson.get('subject')}\n"
        total_lessons += len(grouped['all'])
        if grouped['1'] or grouped['2']:
            message += "\n"

    # Уроки для подгруппы 1
    if grouped['1']:
        message += "🎯 *Подгруппа 1:*\n"
        for i, lesson in enumerate(grouped['1'], 1):
            message += f"  {i}. {lesson.get('time')} - {lesson.get('subject')}\n"
        total_lessons += len(grouped['1'])
        if grouped['2']:
            message += "\n"

    # Уроки для подгруппы 2
    if grouped['2']:
        message += "🎯 *Подгруппа 2:*\n"
        for i, lesson in enumerate(grouped['2'], 1):
            message += f"  {i}. {lesson.get('time')} - {lesson.get('subject')}\n"
        total_lessons += len(grouped['2'])

    message += f"\n📊 Всего уроков: *{total_lessons}*"

    # Статистика по подгруппам
    counts, _ = _format_subgroup_stats(grouped)
    if counts:
        message += f"\n📈 Распределение: {', '.join(counts)}"

    return message


def format_full_schedule_by_days(days_data: dict) -> str:
    """Форматировать полное расписание"""
    if not days_data or not any(lessons for lessons in days_data.values()):
        return "📋 *Ваше расписание*\n\n📭 Расписание пустое!\n\nИспользуйте /add чтобы добавить уроки."

    message = "📋 *Ваше расписание на неделю*\n"
    total_lessons = 0
    subgroup_totals = {'1': 0, '2': 0, 'all': 0}

    for day in DAYS_FULL:
        if day in days_data and days_data[day]:
            lessons = days_data[day]

            # Счетчики
            for lesson in lessons:
                subgroup = lesson.get('subgroup', 'all')
                if subgroup in subgroup_totals:
                    subgroup_totals[subgroup] += 1
                else:
                    subgroup_totals['all'] += 1

            total_lessons += len(lessons)
            emoji = DAY_NUMBER_EMOJIS.get(day, '📅')
            grouped = _format_lessons_by_subgroup(lessons)

            # Статистика по подгруппам для дня
            day_counts = []
            if grouped['all']:
                day_counts.append(f"всех: {len(grouped['all'])}")
            if grouped['1']:
                day_counts.append(f"1: {len(grouped['1'])}")
            if grouped['2']:
                day_counts.append(f"2: {len(grouped['2'])}")

            count_str = f" ({', '.join(day_counts)})" if day_counts else ""
            message += f"\n{emoji} *{day}*{count_str}:\n"

            for lesson in lessons:
                message += f"   {format_lesson_short(lesson)}\n"

    # Итоговая статистика
    message += f"\n📊 *Итого: {total_lessons} уроков*\n"

    subgroup_stats = []
    if subgroup_totals['all'] > 0:
        subgroup_stats.append(f"👥 всех: {subgroup_totals['all']}")
    if subgroup_totals['1'] > 0:
        subgroup_stats.append(f"🎯 1: {subgroup_totals['1']}")
    if subgroup_totals['2'] > 0:
        subgroup_stats.append(f"🎯 2: {subgroup_totals['2']}")

    if subgroup_stats:
        message += f"📈 По подгруппам: {', '.join(subgroup_stats)}"

    return message


def format_week_overview(days_with_lessons: list) -> str:
    """Краткий обзор недели"""
    if not days_with_lessons:
        return "📭 На этой неделе нет уроков. Добавьте первый урок командой /add"

    sorted_days = [day for day in DAYS_FULL if day in days_with_lessons]

    message = "📊 *Обзор недели:*\n"
    for day in sorted_days:
        emoji = DAY_NUMBER_EMOJIS.get(day, '📅')
        message += f"{emoji} {day}\n"

    message += f"\n📈 Всего дней с уроками: *{len(days_with_lessons)}*"
    return message


# === СТАТИСТИКА ===
def format_stats_message(stats: dict) -> str:
    """Форматировать статистику"""
    subgroup = stats.get('subgroup', 'all')
    message = f"📊 *Статистика вашего расписания {SUBGROUP_TEXTS.get(subgroup, '')}*\n\n"

    message += f"• Всего уроков: *{stats.get('total_lessons', 0)}*\n"
    message += f"• Дней с уроками: *{stats.get('days_with_lessons', 0)}*\n"
    message += f"• Разных предметов: *{stats.get('subjects_count', 0)}*\n"

    if stats.get('most_busy_day'):
        message += f"• Самый загруженный день: *{stats['most_busy_day']}*\n"

    # Статистика по дням
    lessons_by_day = stats.get('lessons_by_day', {})
    if lessons_by_day:
        message += "\n📅 *Уроков по дням:*\n"
        for day in DAYS_FULL:
            if day in lessons_by_day:
                count = lessons_by_day[day]
                bars = "█" * min(count, 10)
                message += f"{day[:3]}: {bars} {count}\n"

    return message


# === СПЕЦИАЛЬНЫЕ СООБЩЕНИЯ ===
def format_clear_day_message(day: str, deleted_lessons: list) -> str:
    """Сообщение об очистке дня"""
    if not deleted_lessons:
        return f"📅 В *{day}* не было уроков для удаления."

    grouped = _format_lessons_by_subgroup(deleted_lessons)
    message = f"🗑️ *Удалено из {day}:*\n\n"

    total_deleted = 0

    # Форматирование удаленных уроков
    for subgroup_name, lessons in [('all', '👥 *Для всех подгрупп:*'),
                                   ('1', '🎯 *Подгруппа 1:*'),
                                   ('2', '🎯 *Подгруппа 2:*')]:
        if grouped[subgroup_name]:
            message += f"{lessons}\n"
            for i, lesson in enumerate(grouped[subgroup_name], 1):
                message += f"  {i}. {lesson.get('subject')} в {lesson.get('time')}\n"
            total_deleted += len(grouped[subgroup_name])
            if subgroup_name != '2':
                message += "\n"

    # Статистика
    counts, _ = _format_subgroup_stats(grouped)
    message += f"\n✅ Всего удалено: *{total_deleted}* уроков"

    if counts:
        message += f"\n📈 Распределение: {', '.join(counts)}"

    return message


def format_today_tomorrow_message(day_type: str, day_name: str, lessons: list, subgroup: str = 'all') -> str:
    """Сообщение для сегодня/завтра"""
    day_text = "сегодня" if day_type == "today" else "завтра"
    subgroup_text = SUBGROUP_TEXTS.get(subgroup, '')

    if not lessons:
        if day_type == "today":
            return f"🎉 *{day_name}* {subgroup_text}\n\nСегодня нет уроков для выбранной подгруппы! 🌟"
        else:
            return f"📅 *{day_name}* {subgroup_text}\n\nЗавтра нет уроков для выбранной подгруппы! 😊"

    grouped = _format_lessons_by_subgroup(lessons)
    message = f"📅 *Расписание на {day_text} ({day_name}) {subgroup_text}:*\n\n"
    total_lessons = 0

    # Форматирование по подгруппам
    for subgroup_name, title in [('all', '👥 *Для всех подгрупп:*'),
                                 ('1', '🎯 *Подгруппа 1:*'),
                                 ('2', '🎯 *Подгруппа 2:*')]:
        if grouped[subgroup_name]:
            message += f"{title}\n"
            for i, lesson in enumerate(grouped[subgroup_name], 1):
                message += f"  {i}. {lesson['time']} - {lesson['subject']}\n"
            total_lessons += len(grouped[subgroup_name])
            message += "\n"

    message = message.rstrip("\n") + f"\n\n📊 Всего уроков: *{total_lessons}*"

    # Информация о распределении
    if subgroup == 'all':
        _, stats = _format_subgroup_stats(grouped)
        if stats:
            message += f"\n📈 Распределение: {', '.join(stats)}"

    return message


# === ИНСТРУКЦИИ ===
def format_instruction_message(command: str) -> str:
    """Инструкция по команде"""
    instructions = {
        'add': """
➕ *Как добавить урок (с поддержкой подгрупп):*

*Базовый формат:*
`/add <предмет> <время> <день> [подгруппа]`

*Примеры:*
• `/add Математика 10:00 Понедельник` - для всех
• `/add Математика 10:00 Понедельник 1` - для подгруппы 1
• `/add Математика 10:00 Понедельник 2` - для подгруппы 2
• `/add Математика 10:00 Понедельник all` - для всех подгрупп

*Примечания:*
• Время в формате ЧЧ:ММ (24-часовой)
• День: Понедельник, Вторник и т.д.
• Подгруппа: 1, 2 или all (по умолчанию: all)
• Можно использовать сокращения дней: Пн, Вт, Ср
        """,
        'delete': """
🗑️ *Как удалить урок:*
1. Посмотрите ID урока в расписании
2. Используйте команду:
`/delete <ID_урока>`

*Пример:*
`/delete 5`

*Или:* Используйте кнопку "Удалить урок" в меню
        """,
        'schedule': """
📅 *Как посмотреть расписание (с подгруппами):*

*Команды (показывают для выбранной подгруппы):*
• `/today` - на сегодня
• `/tomorrow` - на завтра  
• `/week` - вся неделя
• `/schedule` - выбрать день
• `/stats` - статистика

*Смена подгруппы:*
• `/subgroup` - выбрать подгруппу (1, 2, all)
• Подгруппа сохраняется индивидуально

*Или:* Используйте кнопки в меню
        """,
        'subgroup': """
🎯 *Как работать с подгруппами:*

*Выбор подгруппы:*
• `/subgroup` - открыть меню выбора
• Каждый пользователь выбирает свою подгруппу
• Подгруппа сохраняется между сессиями

*Доступные варианты:*
• 🎯 Подгруппа 1 - только ваши уроки
• 🎯 Подгруппа 2 - уроки второй подгруппы  
• 👥 Для всех - общие уроки

*Добавление уроков:*
При добавлении укажите подгруппу в конце:
`/add Математика 10:00 Понедельник 1`
        """
    }
    return instructions.get(command, "📖 Инструкция по команде")


def format_subgroup_selection_message(current_subgroup: str = '1') -> str:
    """Сообщение для выбора подгруппы"""
    current_text = {
        '1': '🎯 Подгруппа 1',
        '2': '🎯 Подгруппа 2',
        'all': '👥 Для всех подгрупп'
    }.get(current_subgroup, f'Подгруппа {current_subgroup}')

    return f"""
🎯 *Выбор подгруппы*

Текущая: {current_text}

*Доступные варианты:*
• 🎯 Подгруппа 1 - только ваши индивидуальные уроки
• 🎯 Подгруппа 2 - уроки для второй подгруппы
• 👥 Для всех - общие уроки для всех подгрупп

*Как это работает:*
1. Вы выбираете подгруппу
2. Бот показывает только уроки для этой подгруппы
3. При добавлении урока можно указать подгруппу
4. Каждый пользователь выбирает свою подгруппу

Выберите вашу подгруппу:
"""


# === УТИЛИТНЫЕ СООБЩЕНИЯ ===
def format_success_message(action: str, details: str = "", subgroup: str = None) -> str:
    """Сообщение об успехе"""
    messages = {
        'add': f"✅ Урок успешно добавлен!\n{details}",
        'delete': f"✅ Урок успешно удален!\n{details}",
        'update': f"✅ Урок успешно обновлен!\n{details}",
        'clear': f"✅ День успешно очищен!\n{details}",
        'save': f"✅ Изменения сохранены!\n{details}",
        'subgroup_changed': f"✅ Подгруппа изменена!\n{details}"
    }

    message = messages.get(action, f"✅ Действие выполнено успешно!\n{details}")

    # Добавить информацию о подгруппе
    if subgroup and action in ['add', 'subgroup_changed']:
        subgroup_text = SUBGROUP_TEXTS.get(subgroup, f'подгруппа {subgroup}')
        if action == 'add':
            message += f"\n\n{subgroup_text}"
        elif action == 'subgroup_changed':
            message = message.replace("изменена", f"изменена на {subgroup_text}")

    return message


def format_error_message(error_type: str, details: str = "") -> str:
    """Сообщение об ошибке"""
    errors = {
        'time_format': f"❌ Неверный формат времени!\nИспользуйте ЧЧ:ММ (например: 10:30)\n{details}",
        'missing_args': f"❌ Недостаточно аргументов!\n{details}",
        'lesson_not_found': f"❌ Урок не найден!\n{details}",
        'db_error': f"❌ Ошибка базы данных!\n{details}",
        'invalid_day': f"❌ Неверный день недели!\nИспользуйте: Понедельник, Вторник и т.д.\n{details}",
        'no_lessons': f"❌ Нет уроков для отображения!\n{details}",
        'invalid_subgroup': f"❌ Неверная подгруппа!\nИспользуйте: 1, 2 или all\n{details}",
        'unknown': f"❌ Произошла неизвестная ошибка!\n{details}"
    }
    return errors.get(error_type, errors['unknown'])