# === КОНСТАНТЫ ===
DAYS_FULL = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]

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
    'all': "👥 (для всех подгрупп)"
}


# === ФОРМАТИРОВАНИЕ УРОКОВ ===
def format_lesson_short(lesson: dict) -> str:
    """Краткая информация об уроке"""
    time_str = lesson.get('time', '--:--')
    subject_str = lesson.get('subject', 'Без названия')
    subgroup = lesson.get('subgroup', 'all')

    if subgroup == '1':
        return f"• {time_str} - {subject_str} [1]"
    elif subgroup == '2':
        return f"• {time_str} - {subject_str} [2]"
    else:
        return f"• {time_str} - {subject_str}"


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


# === ФОРМАТИРОВАНИЕ РАСПИСАНИЯ ===
def format_day_schedule(day: str, lessons: list) -> str:
    """Форматировать расписание для дня"""
    if not lessons:
        return f"📅 {day}\n\n🎉 На этот день нет запланированных уроков!"

    emoji = DAY_EMOJIS.get(day, '📅')
    grouped = _format_lessons_by_subgroup(lessons)

    message = f"{emoji} {day}\n\n"
    total_lessons = 0

    # Уроки для всех подгрупп
    if grouped['all']:
        message += "👥 Для всех подгрупп:\n"
        for i, lesson in enumerate(grouped['all'], 1):
            subject = lesson.get('subject', 'Без названия')
            time = lesson.get('time', '--:--')
            message += f"  {i}. {time} - {subject}\n"
        total_lessons += len(grouped['all'])
        if grouped['1'] or grouped['2']:
            message += "\n"

    # Уроки для подгруппы 1
    if grouped['1']:
        message += "🎯 Подгруппа 1:\n"
        for i, lesson in enumerate(grouped['1'], 1):
            subject = lesson.get('subject', 'Без названия')
            time = lesson.get('time', '--:--')
            message += f"  {i}. {time} - {subject}\n"
        total_lessons += len(grouped['1'])
        if grouped['2']:
            message += "\n"

    # Уроки для подгруппы 2
    if grouped['2']:
        message += "🎯 Подгруппа 2:\n"
        for i, lesson in enumerate(grouped['2'], 1):
            subject = lesson.get('subject', 'Без названия')
            time = lesson.get('time', '--:--')
            message += f"  {i}. {time} - {subject}\n"
        total_lessons += len(grouped['2'])

    message += f"\n📊 Всего уроков: {total_lessons}"
    return message


def format_full_schedule_by_days(days_data: dict) -> str:
    """Форматировать полное расписание"""
    if not days_data or not any(lessons for lessons in days_data.values()):
        return "📋 Ваше расписание\n\n📭 Расписание пустое!\n\nИспользуйте /add чтобы добавить уроки."

    message = "📋 Ваше расписание на неделю\n"
    total_lessons = 0

    for day in DAYS_FULL:
        if day in days_data and days_data[day]:
            lessons = days_data[day]
            total_lessons += len(lessons)
            emoji = DAY_NUMBER_EMOJIS.get(day, '📅')

            message += f"\n{emoji} {day}:\n"
            for lesson in lessons:
                message += f"   {format_lesson_short(lesson)}\n"

    message += f"\n📊 Итого: {total_lessons} уроков"
    return message


def format_week_overview(days_with_lessons: list) -> str:
    """Краткий обзор недели"""
    if not days_with_lessons:
        return "📭 На этой неделе нет уроков. Добавьте первый урок командой /add"

    sorted_days = [day for day in DAYS_FULL if day in days_with_lessons]

    message = "📊 Обзор недели:\n"
    for day in sorted_days:
        emoji = DAY_NUMBER_EMOJIS.get(day, '📅')
        message += f"{emoji} {day}\n"

    message += f"\n📈 Всего дней с уроками: {len(sorted_days)}"
    return message


# === СООБЩЕНИЯ ДЛЯ КОМАНД ===
def format_day_command_response(day: str, lessons: list, subgroup: str) -> str:
    """Форматировать ответ для команды дня"""
    if not lessons:
        return f"📅 {day}\n\n🎉 Нет уроков для подгруппы {subgroup}!"

    subgroup_text = SUBGROUP_TEXTS.get(subgroup, f"подгруппа {subgroup}")
    message = f"📅 {day} {subgroup_text}\n\n"

    for i, lesson in enumerate(lessons, 1):
        subject = lesson.get('subject', 'Без названия')
        time = lesson.get('time', '--:--')
        message += f"{i}. {time} - {subject}\n"

    message += f"\n📊 Всего уроков: {len(lessons)}"
    return message


def format_all_lessons_message(all_lessons: list) -> str:
    """Сообщение со всеми уроками"""
    if not all_lessons:
        return "📭 В базе данных нет уроков"

    # Группируем по дням
    lessons_by_day = {}
    for lesson in all_lessons:
        day = lesson.get('day', 'Неизвестно')
        if day not in lessons_by_day:
            lessons_by_day[day] = []
        lessons_by_day[day].append(lesson)

    # Сортируем дни по порядку
    sorted_days = []
    for day in DAYS_FULL:
        if day in lessons_by_day:
            sorted_days.append(day)
    for day in lessons_by_day:
        if day not in sorted_days:
            sorted_days.append(day)

    # Формируем сообщение
    result = "📚 Все уроки в базе данных:\n\n"
    total_lessons = 0

    for day in sorted_days:
        lessons = lessons_by_day[day]
        total_lessons += len(lessons)

        result += f"\n📅 {day.upper()}\n"

        # Сортируем уроки по времени
        lessons.sort(key=lambda x: x.get('time', '00:00'))

        for lesson in lessons:
            time = lesson.get('time', '??:??')
            subject = lesson.get('subject', 'Неизвестно')
            subgroup = lesson.get('subgroup', 'all')

            if subgroup == '1':
                result += f"🕒 {time} - {subject} [1]\n"
            elif subgroup == '2':
                result += f"🕒 {time} - {subject} [2]\n"
            else:
                result += f"🕒 {time} - {subject}\n"

    result += f"\n📊 Всего уроков в базе: {total_lessons}"
    return result


# === ТЕКСТОВЫЕ СООБЩЕНИЯ ===
def get_help_message() -> str:
    """Полное сообщение помощи"""
    return (
        "🆘 СПРАВКА ПО КОМАНДАМ\n\n"

        "🎯 ВЫБОР ПОДГРУППЫ:\n"
        "/subgroup_1 - Подгруппа 1\n"
        "/subgroup_2 - Подгруппа 2\n"
        "/subgroup_all - Для всех подгрупп\n\n"

        "📅 РАСПИСАНИЕ ПО ДНЯМ:\n"
        "/day_monday - Понедельник\n"
        "/day_tuesday - Вторник\n"
        "/day_wednesday - Среда\n"
        "/day_thursday - Четверг\n"
        "/day_friday - Пятница\n"
        "/day_saturday - Суббота\n"
        "/day_sunday - Воскресенье\n\n"

        "📋 ОСНОВНЫЕ КОМАНДЫ:\n"
        "/start - Начать работу с ботом\n"
        "/today - Расписание на сегодня\n"
        "/tomorrow - Расписание на завтра\n"
        "/week - Вся неделя\n"
        "/all - Все уроки в базе\n"
        "/schedule - Показать список дней\n"
        "/subgroup - Показать список подгрупп\n"
        "/help - Эта справка\n\n"

        "➕ ДОБАВЛЕНИЕ УРОКА:\n"
        "/add Математика 10:00 Понедельник\n"
        "/add Математика 10:00 Понедельник 1\n"
        "/add Математика 10:00 Понедельник 2\n"
        "/add Математика 10:00 Понедельник all\n\n"

        "🗑️ УДАЛЕНИЕ УРОКА:\n"
        "/delete 1 - Удалить урок с ID=1\n"
        "После /delete используйте:\n"
        "/confirm_delete_1 - чтобы подтвердить\n"
        "/cancel - чтобы отменить\n\n"

        "⚙️ ДОПОЛНИТЕЛЬНО:\n"
        "/clearcache - Очистить кэш\n\n"

        "💡 СОВЕТЫ:\n"
        "• Используйте кнопки внизу экрана\n"
        "• Подгруппа: 1, 2 или all\n"
        "• Дни: Понедельник-Воскресенье"
    )


def get_days_list_message(subgroup: str = '1') -> str:
    """Сообщение со списком дней"""
    message = "📅 Доступные команды для дней:\n\n"
    for day in DAYS_FULL:
        day_lower = day.lower()
        message += f"• /day_{day_lower} - {day}\n"
    message += f"\n✨ Пример: /day_monday\n"
    message += f"🎯 Текущая подгруппа: {subgroup}"
    return message


def get_subgroups_list_message() -> str:
    """Сообщение со списком подгрупп"""
    return (
        "🎯 Доступные команды подгрупп:\n\n"
        "• /subgroup_1 - Подгруппа 1\n"
        "• /subgroup_2 - Подгруппа 2\n"
        "• /subgroup_all - Для всех подгрупп\n\n"
        "✨ Пример: /subgroup_1\n"
        "🔄 Подгруппа сохраняется индивидуально для каждого пользователя"
    )


def get_add_instruction_message() -> str:
    """Инструкция по добавлению урока"""
    return (
        "📝 Формат: /add <предмет> <время> <день> [подгруппа]\n\n"
        "📌 Примеры:\n"
        "• /add Математика 10:00 Понедельник - для всех\n"
        "• /add Математика 10:00 Понедельник 1 - для подгруппы 1\n"
        "• /add Математика 10:00 Понедельник 2 - для подгруппы 2\n"
        "• /add Математика 10:00 Понедельник all - для всех подгрупп\n\n"
        "⚠️ Подгруппа по умолчанию: all"
    )


def format_delete_confirmation_message(lesson: dict) -> str:
    """Сообщение подтверждения удаления"""
    subject = lesson.get('subject', 'Неизвестно')
    time = lesson.get('time', 'Неизвестно')
    day = lesson.get('day', 'Неизвестно')
    subgroup = lesson.get('subgroup', 'all')
    lesson_id = str(lesson.get('id', 'Неизвестно'))

    subgroup_text = SUBGROUP_TEXTS.get(subgroup, f"подгруппа {subgroup}")

    message = "🗑️ Удалить урок?\n\n"
    message += f"• Предмет: {subject}\n"
    message += f"• Время: {time}\n"
    message += f"• День: {day}\n"
    message += f"• Подгруппа: {subgroup_text}\n"
    message += f"• ID: {lesson_id}\n\n"
    message += f"📝 Для подтверждения напишите:\n"
    message += f"/confirm_delete_{lesson_id} - удалить\n"
    message += "/cancel - отменить"

    return message