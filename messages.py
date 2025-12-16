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


def format_lesson_message(lesson: dict) -> str:
    """Форматирует информацию об одной паре с подгруппой"""
    message = f"📚 *{lesson.get('subject', 'Без названия')}*\n"
    message += f"🕗 Время: {lesson.get('time', '--:--')}\n"
    message += f"📆 День: {lesson.get('day', 'Не указан')}\n"

    # Добавляем информацию о подгруппе
    subgroup = lesson.get('subgroup', 'all')
    if subgroup == '1':
        message += "🎯 Подгруппа: 1\n"
    elif subgroup == '2':
        message += "🎯 Подгруппа: 2\n"
    else:
        message += "👥 Для всех подгрупп\n"

    message += f"🆔 ID: {lesson.get('id', '?')}"
    return message


def format_lesson_short(lesson: dict) -> str:
    """Краткая информация об уроке с указанием подгруппы"""
    time_str = lesson.get('time', '--:--')
    subject_str = lesson.get('subject', 'Без названия')

    # Добавляем маркер подгруппы
    subgroup = lesson.get('subgroup', 'all')
    if subgroup == '1':
        subgroup_mark = " [1]"
    elif subgroup == '2':
        subgroup_mark = " [2]"
    else:
        subgroup_mark = ""

    return f"• {time_str} - {subject_str}{subgroup_mark}"


def format_day_schedule(day: str, lessons: list) -> str:
    """Форматирование расписания для конкретного дня"""
    if not lessons:
        return f"📅 *{day}*\n\n🎉 На этот день нет запланированных уроков!"

    # Эмодзи для дней
    day_emojis = {
        'Понедельник': '📅',
        'Вторник': '📅',
        'Среда': '📅',
        'Четверг': '📅',
        'Пятница': '📅',
        'Суббота': '🎉',
        'Воскресенье': '🌟'
    }

    emoji = day_emojis.get(day, '📅')
    message = f"{emoji} *{day}*\n\n"

    # Группируем уроки по подгруппам для лучшей читаемости
    lessons_by_subgroup = {'1': [], '2': [], 'all': []}
    for lesson in lessons:
        subgroup = lesson.get('subgroup', 'all')
        lessons_by_subgroup[subgroup].append(lesson)

    total_lessons = 0

    # Показываем уроки для всех подгрупп
    if lessons_by_subgroup['all']:
        message += "👥 *Для всех подгрупп:*\n"
        for i, lesson in enumerate(lessons_by_subgroup['all'], 1):
            message += f"  {i}. {lesson.get('time')} - {lesson.get('subject')}\n"
        total_lessons += len(lessons_by_subgroup['all'])
        if lessons_by_subgroup['1'] or lessons_by_subgroup['2']:
            message += "\n"

    # Показываем уроки для подгруппы 1
    if lessons_by_subgroup['1']:
        message += "🎯 *Подгруппа 1:*\n"
        for i, lesson in enumerate(lessons_by_subgroup['1'], 1):
            message += f"  {i}. {lesson.get('time')} - {lesson.get('subject')}\n"
        total_lessons += len(lessons_by_subgroup['1'])
        if lessons_by_subgroup['2']:
            message += "\n"

    # Показываем уроки для подгруппы 2
    if lessons_by_subgroup['2']:
        message += "🎯 *Подгруппа 2:*\n"
        for i, lesson in enumerate(lessons_by_subgroup['2'], 1):
            message += f"  {i}. {lesson.get('time')} - {lesson.get('subject')}\n"
        total_lessons += len(lessons_by_subgroup['2'])

    message += f"\n📊 Всего уроков: *{total_lessons}*"

    # Добавляем информацию о распределении по подгруппам
    subgroup_counts = []
    if lessons_by_subgroup['all']:
        subgroup_counts.append(f"для всех: {len(lessons_by_subgroup['all'])}")
    if lessons_by_subgroup['1']:
        subgroup_counts.append(f"подгр.1: {len(lessons_by_subgroup['1'])}")
    if lessons_by_subgroup['2']:
        subgroup_counts.append(f"подгр.2: {len(lessons_by_subgroup['2'])}")

    if subgroup_counts:
        message += f"\n📈 Распределение: {', '.join(subgroup_counts)}"

    return message


def format_full_schedule_by_days(days_data: dict) -> str:
    """Форматирование полного расписания по дням с подгруппами"""
    if not days_data or not any(lessons for lessons in days_data.values()):
        return "📋 *Ваше расписание*\n\n📭 Расписание пустое!\n\nИспользуйте /add чтобы добавить уроки."

    # Порядок дней недели
    days_order = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресеньe']

    message = "📋 *Ваше расписание на неделю*\n"
    total_lessons = 0

    # Подсчет уроков по подгруппам
    subgroup_totals = {'1': 0, '2': 0, 'all': 0}

    for day in days_order:
        if day in days_data and days_data[day]:
            lessons = days_data[day]

            # Подсчитываем уроки по подгруппам
            for lesson in lessons:
                subgroup = lesson.get('subgroup', 'all')
                subgroup_totals[subgroup] += 1

            total_lessons += len(lessons)

            # Эмодзи для дней
            day_emojis = {
                'Понедельник': '1️⃣',
                'Вторник': '2️⃣',
                'Среда': '3️⃣',
                'Четверг': '4️⃣',
                'Пятница': '5️⃣',
                'Суббота': '6️⃣',
                'Воскресенье': '7️⃣'
            }

            emoji = day_emojis.get(day, '📅')

            # Считаем уроки по подгруппам для этого дня
            day_subgroup_counts = {'1': 0, '2': 0, 'all': 0}
            for lesson in lessons:
                subgroup = lesson.get('subgroup', 'all')
                day_subgroup_counts[subgroup] += 1

            # Формируем строку с количеством уроков по подгруппам
            day_counts = []
            if day_subgroup_counts['all'] > 0:
                day_counts.append(f"всех: {day_subgroup_counts['all']}")
            if day_subgroup_counts['1'] > 0:
                day_counts.append(f"1: {day_subgroup_counts['1']}")
            if day_subgroup_counts['2'] > 0:
                day_counts.append(f"2: {day_subgroup_counts['2']}")

            count_str = f" ({', '.join(day_counts)})" if day_counts else ""

            message += f"\n{emoji} *{day}*{count_str}:\n"

            for lesson in lessons:
                message += f"   {format_lesson_short(lesson)}\n"

    # Добавляем итоговую статистику по подгруппам
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

    # Сортируем дни по порядку недели
    days_order = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    sorted_days = [day for day in days_order if day in days_with_lessons]

    # Эмодзи для дней
    day_emojis = {
        'Понедельник': '1️⃣',
        'Вторник': '2️⃣',
        'Среда': '3️⃣',
        'Четверг': '4️⃣',
        'Пятница': '5️⃣',
        'Суббота': '6️⃣',
        'Воскресенье': '7️⃣'
    }

    message = "📊 *Обзор недели:*\n"
    for day in sorted_days:
        emoji = day_emojis.get(day, '📅')
        message += f"{emoji} {day}\n"

    message += f"\n📈 Всего дней с уроками: *{len(days_with_lessons)}*"
    return message


def format_stats_message(stats: dict) -> str:
    """Форматирование статистики с информацией о подгруппе"""
    subgroup = stats.get('subgroup', 'all')
    subgroup_text = {
        '1': '(подгруппа 1)',
        '2': '(подгруппа 2)',
        'all': '(все подгруппы)'
    }.get(subgroup, '')

    message = f"📊 *Статистика вашего расписания {subgroup_text}*\n\n"

    message += f"• Всего уроков: *{stats.get('total_lessons', 0)}*\n"
    message += f"• Дней с уроками: *{stats.get('days_with_lessons', 0)}*\n"
    message += f"• Разных предметов: *{stats.get('subjects_count', 0)}*\n"

    if stats.get('most_busy_day'):
        message += f"• Самый загруженный день: *{stats['most_busy_day']}*\n"

    # Статистика по дням
    lessons_by_day = stats.get('lessons_by_day', {})
    if lessons_by_day:
        message += "\n📅 *Уроков по дням:*\n"
        days_order = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
        for day in days_order:
            if day in lessons_by_day:
                count = lessons_by_day[day]
                bars = "█" * min(count, 10)  # Максимум 10 полосок
                message += f"{day[:3]}: {bars} {count}\n"

    return message


def format_stats_for_subgroup(stats: dict, subgroup: str) -> str:
    """Форматирование статистики для конкретной подгруппы"""
    subgroup_name = {
        '1': '🎯 Подгруппа 1',
        '2': '🎯 Подгруппа 2',
        'all': '👥 Все подгруппы'
    }.get(subgroup, f'Подгруппа {subgroup}')

    message = f"{subgroup_name}\n\n"
    message += f"📊 Уроков: *{stats.get('total_lessons', 0)}*\n"
    message += f"📅 Дней: *{stats.get('days_with_lessons', 0)}*\n"
    message += f"📚 Предметов: *{stats.get('subjects_count', 0)}*\n"

    if stats.get('most_busy_day'):
        message += f"🏆 Самый загруженный: *{stats['most_busy_day']}*\n"

    return message


def format_clear_day_message(day: str, deleted_lessons: list) -> str:
    """Сообщение об очистке дня"""
    if not deleted_lessons:
        return f"📅 В *{day}* не было уроков для удаления."

    # Группируем удаленные уроки по подгруппам
    deleted_by_subgroup = {'1': [], '2': [], 'all': []}
    for lesson in deleted_lessons:
        subgroup = lesson.get('subgroup', 'all')
        deleted_by_subgroup[subgroup].append(lesson)

    message = f"🗑️ *Удалено из {day}:*\n\n"

    total_deleted = 0

    # Уроки для всех подгрупп
    if deleted_by_subgroup['all']:
        message += "👥 *Для всех подгрупп:*\n"
        for i, lesson in enumerate(deleted_by_subgroup['all'], 1):
            message += f"  {i}. {lesson.get('subject')} в {lesson.get('time')}\n"
        total_deleted += len(deleted_by_subgroup['all'])
        if deleted_by_subgroup['1'] or deleted_by_subgroup['2']:
            message += "\n"

    # Уроки для подгруппы 1
    if deleted_by_subgroup['1']:
        message += "🎯 *Подгруппа 1:*\n"
        for i, lesson in enumerate(deleted_by_subgroup['1'], 1):
            message += f"  {i}. {lesson.get('subject')} в {lesson.get('time')}\n"
        total_deleted += len(deleted_by_subgroup['1'])
        if deleted_by_subgroup['2']:
            message += "\n"

    # Уроки для подгруппы 2
    if deleted_by_subgroup['2']:
        message += "🎯 *Подгруппа 2:*\n"
        for i, lesson in enumerate(deleted_by_subgroup['2'], 1):
            message += f"  {i}. {lesson.get('subject')} в {lesson.get('time')}\n"
        total_deleted += len(deleted_by_subgroup['2'])

    # Подсчет по подгруппам
    subgroup_counts = []
    if deleted_by_subgroup['all']:
        subgroup_counts.append(f"для всех: {len(deleted_by_subgroup['all'])}")
    if deleted_by_subgroup['1']:
        subgroup_counts.append(f"подгр.1: {len(deleted_by_subgroup['1'])}")
    if deleted_by_subgroup['2']:
        subgroup_counts.append(f"подгр.2: {len(deleted_by_subgroup['2'])}")

    message += f"\n✅ Всего удалено: *{total_deleted}* уроков"

    if subgroup_counts:
        message += f"\n📈 Распределение: {', '.join(subgroup_counts)}"

    return message


def format_success_message(action: str, details: str = "", subgroup: str = None) -> str:
    """Сообщение об успешном выполнении с подгруппой"""
    messages = {
        'add': f"✅ Урок успешно добавлен!\n{details}",
        'delete': f"✅ Урок успешно удален!\n{details}",
        'update': f"✅ Урок успешно обновлен!\n{details}",
        'clear': f"✅ День успешно очищен!\n{details}",
        'save': f"✅ Изменения сохранены!\n{details}",
        'subgroup_changed': f"✅ Подгруппа изменена!\n{details}"
    }

    base_message = messages.get(action, f"✅ Действие выполнено успешно!\n{details}")

    # Добавляем информацию о подгруппе если есть
    if subgroup and action in ['add', 'subgroup_changed']:
        subgroup_text = {
            '1': '🎯 (подгруппа 1)',
            '2': '🎯 (подгруппа 2)',
            'all': '👥 (для всех подгрупп)'
        }.get(subgroup, f'подгруппа {subgroup}')

        if action == 'add':
            base_message += f"\n\n{subgroup_text}"
        elif action == 'subgroup_changed':
            base_message = base_message.replace("изменена", f"изменена на {subgroup_text}")

    return base_message


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


def format_today_tomorrow_message(day_type: str, day_name: str, lessons: list, subgroup: str = 'all') -> str:
    """Сообщение для сегодня/завтра с подгруппой"""
    day_text = "сегодня" if day_type == "today" else "завтра"
    subgroup_text = {
        '1': '(подгруппа 1)',
        '2': '(подгруппа 2)',
        'all': ''
    }.get(subgroup, '')

    if not lessons:
        if day_type == "today":
            return f"🎉 *{day_name}* {subgroup_text}\n\nСегодня нет уроков для выбранной подгруппы! 🌟"
        else:
            return f"📅 *{day_name}* {subgroup_text}\n\nЗавтра нет уроков для выбранной подгруппы! 😊"

    message = f"📅 *Расписание на {day_text} ({day_name}) {subgroup_text}:*\n\n"

    # Группируем уроки по подгруппам
    lessons_by_subgroup = {'1': [], '2': [], 'all': []}
    for lesson in lessons:
        lesson_subgroup = lesson.get('subgroup', 'all')
        lessons_by_subgroup[lesson_subgroup].append(lesson)

    total_lessons = 0

    # Показываем уроки для всех подгрупп
    if lessons_by_subgroup['all']:
        message += "👥 *Для всех подгрупп:*\n"
        for i, lesson in enumerate(lessons_by_subgroup['all'], 1):
            message += f"  {i}. {lesson['time']} - {lesson['subject']}\n"
        total_lessons += len(lessons_by_subgroup['all'])
        if lessons_by_subgroup['1'] or lessons_by_subgroup['2']:
            message += "\n"

    # Показываем уроки для подгруппы 1
    if lessons_by_subgroup['1']:
        message += "🎯 *Подгруппа 1:*\n"
        for i, lesson in enumerate(lessons_by_subgroup['1'], 1):
            message += f"  {i}. {lesson['time']} - {lesson['subject']}\n"
        total_lessons += len(lessons_by_subgroup['1'])
        if lessons_by_subgroup['2']:
            message += "\n"

    # Показываем уроки для подгруппы 2
    if lessons_by_subgroup['2']:
        message += "🎯 *Подгруппа 2:*\n"
        for i, lesson in enumerate(lessons_by_subgroup['2'], 1):
            message += f"  {i}. {lesson['time']} - {lesson['subject']}\n"
        total_lessons += len(lessons_by_subgroup['2'])

    message += f"\n📊 Всего уроков: *{total_lessons}*"

    # Информация о подгруппах
    if subgroup == 'all' and (lessons_by_subgroup['1'] or lessons_by_subgroup['2']):
        subgroup_info = []
        if lessons_by_subgroup['1']:
            subgroup_info.append(f"подгр.1: {len(lessons_by_subgroup['1'])}")
        if lessons_by_subgroup['2']:
            subgroup_info.append(f"подгр.2: {len(lessons_by_subgroup['2'])}")
        if lessons_by_subgroup['all']:
            subgroup_info.append(f"всех: {len(lessons_by_subgroup['all'])}")

        if subgroup_info:
            message += f"\n📈 Распределение: {', '.join(subgroup_info)}"

    return message


def format_instruction_message(command: str) -> str:
    """Инструкция по использованию команды с подгруппами"""
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