# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ДЛЯ MARKDOWN ===
def escape_markdown_v2(text: str) -> str:
    """Экранирует специальные символы для MarkdownV2"""
    if not text:
        return ""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text


def safe_markdown_bold(text: str) -> str:
    """Возвращает текст в жирном начертании с экранированием"""
    return f"*{escape_markdown_v2(text)}*"


# === КОНСТАНТЫ ===
DAYS_FULL = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
DAYS_COMMANDS = {
    'понедельник': 'Понедельник',
    'вторник': 'Вторник',
    'среда': 'Среда',
    'четверг': 'Четверг',
    'пятница': 'Пятница',
    'суббота': 'Суббота',
    'воскресенье': 'Воскресенье'
}

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


# === СПРАВОЧНЫЕ СООБЩЕНИЯ ===
def get_help_message() -> str:
    """Полное сообщение помощи"""
    return (
        "🆘 *СПРАВКА ПО КОМАНДАМ*\n\n"

        "🎯 *ВЫБОР ПОДГРУППЫ:*\n"
        "`/subgroup_1` - Подгруппа 1\n"
        "`/subgroup_2` - Подгруппа 2\n"
        "`/subgroup_all` - Для всех подгрупп\n\n"

        "📅 *РАСПИСАНИЕ ПО ДНЯМ:*\n"
        "`/day_понедельник` - Понедельник\n"
        "`/day_вторник` - Вторник\n"
        "`/day_среда` - Среда\n"
        "`/day_четверг` - Четверг\n"
        "`/day_пятница` - Пятница\n"
        "`/day_суббота` - Суббота\n"
        "`/day_воскресенье` - Воскресенье\n\n"

        "📋 *ОСНОВНЫЕ КОМАНДЫ:*\n"
        "`/start` - Начать работу с ботом\n"
        "`/today` - Расписание на сегодня\n"
        "`/tomorrow` - Расписание на завтра\n"
        "`/week` - Вся неделя\n"
        "`/all` - Все уроки в базе\n"
        "`/schedule` - Показать список дней\n"
        "`/subgroup` - Показать список подгрупп\n"
        "`/help` - Эта справка\n\n"

        "➕ *ДОБАВЛЕНИЕ УРОКА:*\n"
        "`/add Математика 10:00 Понедельник`\n"
        "`/add Математика 10:00 Понедельник 1`\n"
        "`/add Математика 10:00 Понедельник 2`\n"
        "`/add Математика 10:00 Понедельник all`\n\n"

        "🗑️ *УДАЛЕНИЕ УРОКА:*\n"
        "`/delete 1` - Удалить урок с ID=1\n"
        "После `/delete` используйте:\n"
        "`/confirm_delete_1` - чтобы подтвердить\n"
        "`/cancel` - чтобы отменить\n\n"

        "⚙️ *ДОПОЛНИТЕЛЬНО:*\n"
        "`/clearcache` - Очистить кэш\n\n"

        "💡 *СОВЕТЫ:*\n"
        "• Используйте кнопки внизу экрана\n"
        "• Подгруппа: 1, 2 или all\n"
        "• Дни: Понедельник-Воскресенье"
    )


def get_welcome_message(subgroup: str = '1') -> str:
    """Приветственное сообщение"""
    subgroup_text = SUBGROUP_TEXTS.get(subgroup, f"подгруппа {subgroup}")
    return (
        f"👋 Добро пожаловать в бот-расписание!\n\n"
        f"🎯 *Текущая подгруппа:* {subgroup_text}\n\n"
        f"📌 *Быстрый старт:*\n"
        f"1. Посмотреть расписание: `/today` или `/week`\n"
        f"2. Сменить подгруппу: `/subgroup_1`, `/subgroup_2`, `/subgroup_all`\n"
        f"3. Добавить урок: `/add Математика 10:00 Понедельник`\n\n"
        f"❓ Полный список команд: `/help`"
    )


def get_days_list_message(subgroup: str = '1') -> str:
    """Сообщение со списком дней"""
    message = "📅 *Доступные команды для дней:*\n\n"
    for day_command, day_name in DAYS_COMMANDS.items():
        message += f"• `/day_{day_command}` - {day_name}\n"
    message += f"\n✨ Пример: `/day_понедельник`\n"
    message += f"🎯 Текущая подгруппа: {subgroup}"
    return message


def get_subgroups_list_message() -> str:
    """Сообщение со списком подгрупп"""
    return (
        "🎯 *Доступные команды подгрупп:*\n\n"
        "• `/subgroup_1` - Подгруппа 1\n"
        "• `/subgroup_2` - Подгруппа 2\n"
        "• `/subgroup_all` - Для всех подгрупп\n\n"
        "✨ *Пример:* `/subgroup_1`\n"
        "🔄 Подгруппа сохраняется индивидуально для каждого пользователя"
    )


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


# === ФОРМАТИРОВАНИЕ УРОКОВ ===
def format_lesson_message(lesson: dict) -> str:
    """Форматировать информацию об уроке"""
    subject = escape_markdown_v2(lesson.get('subject', 'Без названия'))
    time = escape_markdown_v2(lesson.get('time', '--:--'))
    day = escape_markdown_v2(lesson.get('day', 'Не указан'))
    subgroup = lesson.get('subgroup', 'all')
    lesson_id = escape_markdown_v2(str(lesson.get('id', '?')))

    subgroup_text = SUBGROUP_TEXTS.get(subgroup, f"Подгруппа: {escape_markdown_v2(subgroup)}")

    return f"""📚 {safe_markdown_bold(subject)}
🕗 Время: {time}
📆 День: {day}
{subgroup_text}
🆔 ID: {lesson_id}"""


def format_lesson_short(lesson: dict) -> str:
    """Краткая информация об уроке"""
    time_str = escape_markdown_v2(lesson.get('time', '--:--'))
    subject_str = escape_markdown_v2(lesson.get('subject', 'Без названия'))
    return f"• {time_str} - {subject_str}{_get_subgroup_mark(lesson.get('subgroup', 'all'))}"


# === ФОРМАТИРОВАНИЕ РАСПИСАНИЯ ===
def format_day_schedule(day: str, lessons: list) -> str:
    """Форматировать расписание для дня"""
    safe_day = escape_markdown_v2(day)
    if not lessons:
        return f"📅 {safe_markdown_bold(day)}\n\n🎉 На этот день нет запланированных уроков!"

    emoji = DAY_EMOJIS.get(day, '📅')
    grouped = _format_lessons_by_subgroup(lessons)

    message = f"{emoji} {safe_markdown_bold(day)}\n\n"
    total_lessons = 0

    # Уроки для всех подгрупп
    if grouped['all']:
        message += "👥 *Для всех подгрупп:*\n"
        for i, lesson in enumerate(grouped['all'], 1):
            subject = escape_markdown_v2(lesson.get('subject', 'Без названия'))
            time = escape_markdown_v2(lesson.get('time', '--:--'))
            message += f"  {escape_markdown_v2(str(i))}. {time} - {subject}\n"
        total_lessons += len(grouped['all'])
        if grouped['1'] or grouped['2']:
            message += "\n"

    # Уроки для подгруппы 1
    if grouped['1']:
        message += "🎯 *Подгруппа 1:*\n"
        for i, lesson in enumerate(grouped['1'], 1):
            subject = escape_markdown_v2(lesson.get('subject', 'Без названия'))
            time = escape_markdown_v2(lesson.get('time', '--:--'))
            message += f"  {escape_markdown_v2(str(i))}. {time} - {subject}\n"
        total_lessons += len(grouped['1'])
        if grouped['2']:
            message += "\n"

    # Уроки для подгруппы 2
    if grouped['2']:
        message += "🎯 *Подгруппа 2:*\n"
        for i, lesson in enumerate(grouped['2'], 1):
            subject = escape_markdown_v2(lesson.get('subject', 'Без названия'))
            time = escape_markdown_v2(lesson.get('time', '--:--'))
            message += f"  {escape_markdown_v2(str(i))}. {time} - {subject}\n"
        total_lessons += len(grouped['2'])

    message += f"\n📊 Всего уроков: {safe_markdown_bold(str(total_lessons))}"

    # Статистика по подгруппам
    counts = []
    if grouped['all']:
        counts.append(f"всех: {escape_markdown_v2(str(len(grouped['all'])))}")
    if grouped['1']:
        counts.append(f"1: {escape_markdown_v2(str(len(grouped['1'])))}")
    if grouped['2']:
        counts.append(f"2: {escape_markdown_v2(str(len(grouped['2'])))}")

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
                day_counts.append(f"всех: {escape_markdown_v2(str(len(grouped['all'])))}")
            if grouped['1']:
                day_counts.append(f"1: {escape_markdown_v2(str(len(grouped['1'])))}")
            if grouped['2']:
                day_counts.append(f"2: {escape_markdown_v2(str(len(grouped['2'])))}")

            safe_day = escape_markdown_v2(day)
            count_str = f" ({', '.join(day_counts)})" if day_counts else ""
            message += f"\n{emoji} {safe_markdown_bold(day)}{count_str}:\n"

            for lesson in lessons:
                message += f"   {format_lesson_short(lesson)}\n"

    # Итоговая статистика
    message += f"\n📊 *Итого: {escape_markdown_v2(str(total_lessons))} уроков*\n"

    subgroup_stats = []
    if subgroup_totals['all'] > 0:
        subgroup_stats.append(f"👥 всех: {escape_markdown_v2(str(subgroup_totals['all']))}")
    if subgroup_totals['1'] > 0:
        subgroup_stats.append(f"🎯 1: {escape_markdown_v2(str(subgroup_totals['1']))}")
    if subgroup_totals['2'] > 0:
        subgroup_stats.append(f"🎯 2: {escape_markdown_v2(str(subgroup_totals['2']))}")

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
        safe_day = escape_markdown_v2(day)
        message += f"{emoji} {safe_day}\n"

    message += f"\n📈 Всего дней с уроками: {safe_markdown_bold(str(len(days_with_lessons)))}"
    return message


# === СООБЩЕНИЯ ДЛЯ КОМАНД ===
def format_day_command_response(day: str, lessons: list, subgroup: str) -> str:
    """Форматировать ответ для команды дня"""
    if not lessons:
        return f"📅 {safe_markdown_bold(day)}\n\n🎉 Нет уроков для подгруппы {escape_markdown_v2(subgroup)}!"

    subgroup_text = SUBGROUP_TEXTS.get(subgroup, f"подгруппа {escape_markdown_v2(subgroup)}")
    message = f"📅 {safe_markdown_bold(day)} {subgroup_text}\n\n"

    for i, lesson in enumerate(lessons, 1):
        subject = escape_markdown_v2(lesson.get('subject', 'Без названия'))
        time = escape_markdown_v2(lesson.get('time', '--:--'))
        message += f"{escape_markdown_v2(str(i))}. {time} - {subject}\n"

    message += f"\n📊 Всего уроков: {safe_markdown_bold(str(len(lessons)))}"
    return message


def format_subgroup_changed_message(subgroup: str) -> str:
    """Сообщение об изменении подгруппы"""
    subgroup_text = SUBGROUP_TEXTS.get(subgroup, f"подгруппа {escape_markdown_v2(subgroup)}")
    return f"✅ Выбрана {subgroup_text}\n\nТеперь вы будете видеть уроки только для этой подгруппы."


def format_delete_confirmation_message(lesson: dict) -> str:
    """Сообщение подтверждения удаления"""
    subject = escape_markdown_v2(lesson.get('subject', 'Неизвестно'))
    time = escape_markdown_v2(lesson.get('time', 'Неизвестно'))
    day = escape_markdown_v2(lesson.get('day', 'Неизвестно'))
    subgroup = lesson.get('subgroup', 'all')
    lesson_id = escape_markdown_v2(str(lesson.get('id', 'Неизвестно')))

    subgroup_text = SUBGROUP_TEXTS.get(subgroup, f"подгруппа {escape_markdown_v2(subgroup)}")

    message = "🗑️ *Удалить урок?*\n\n"
    message += f"• Предмет: {subject}\n"
    message += f"• Время: {time}\n"
    message += f"• День: {day}\n"
    message += f"• Подгруппа: {subgroup_text}\n"
    message += f"• ID: {lesson_id}\n\n"
    message += f"📝 *Для подтверждения напишите:*\n"
    message += f"`/confirm_delete_{lesson.get('id', '')}` - удалить\n"
    message += "`/cancel` - отменить"

    return message


def format_add_instruction_message() -> str:
    """Инструкция по добавлению урока"""
    return (
        "📝 *Формат:* `/add <предмет> <время> <день> [подгруппа]`\n\n"
        "📌 *Примеры:*\n"
        "• `/add Математика 10:00 Понедельник` - для всех\n"
        "• `/add Математика 10:00 Понедельник 1` - для подгруппы 1\n"
        "• `/add Математика 10:00 Понедельник 2` - для подгруппы 2\n"
        "• `/add Математика 10:00 Понедельник all` - для всех подгрупп\n\n"
        "⚠️ *Подгруппа по умолчанию:* `all`"
    )


# === СООБЩЕНИЯ ОБ УСПЕХЕ/ОШИБКАХ ===
def format_success_message(action: str, details: str = "") -> str:
    """Сообщение об успехе"""
    safe_details = escape_markdown_v2(details)

    messages = {
        'add': f"✅ Урок успешно добавлен!\n{safe_details}",
        'delete': f"✅ Урок успешно удален!\n{safe_details}",
        'subgroup_changed': f"✅ Подгруппа изменена!\n{safe_details}",
        'cache_cleared': "✅ Кэш расписания очищен"
    }

    return messages.get(action, f"✅ Действие выполнено успешно!\n{safe_details}")


def format_error_message(error_type: str, details: str = "") -> str:
    """Сообщение об ошибке"""
    safe_details = escape_markdown_v2(details)

    errors = {
        'time_format': f"❌ Неверный формат времени!\nИспользуйте ЧЧ:ММ (например: 10:30)\n{safe_details}",
        'missing_args': f"❌ Недостаточно аргументов!\n{safe_details}",
        'lesson_not_found': f"❌ Урок не найден!\n{safe_details}",
        'db_error': f"❌ Ошибка базы данных!\n{safe_details}",
        'invalid_day': f"❌ Неверный день недели!\nИспользуйте: Понедельник, Вторник и т.д.\n{safe_details}",
        'no_lessons': f"❌ Нет уроков для отображения!\n{safe_details}",
        'invalid_subgroup': f"❌ Неверная подгруппа!\nИспользуйте: 1, 2 или all\n{safe_details}",
        'unknown': f"❌ Произошла неизвестная ошибка!\n{safe_details}"
    }
    return errors.get(error_type, errors['unknown'])


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
    result = "📚 *Все уроки в базе данных:*\n\n"
    total_lessons = 0

    for day in sorted_days:
        lessons = lessons_by_day[day]
        total_lessons += len(lessons)

        result += f"\n📅 {safe_markdown_bold(day.upper())}\n"

        # Сортируем уроки по времени
        lessons.sort(key=lambda x: x.get('time', '00:00'))

        for lesson in lessons:
            time = escape_markdown_v2(lesson.get('time', '??:??'))
            subject = escape_markdown_v2(lesson.get('subject', 'Неизвестно'))
            subgroup = lesson.get('subgroup', 'all')

            subgroup_mark = _get_subgroup_mark(subgroup)
            result += f"🕒 {time} - {subject}{subgroup_mark}\n"

    result += f"\n📊 Всего уроков в базе: {safe_markdown_bold(str(total_lessons))}"
    return result