import os
import datetime
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
from database import ScheduleDatabase
from keyboards import create_main_menu, create_confirmation_keyboard, create_day_selection_keyboard, \
    create_subgroup_selection_keyboard
from messages import format_day_schedule, format_full_schedule_by_days, format_week_overview

# === НАСТРОЙКА ЛОГГИРОВАНИЯ ===
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    datefmt='%H:%M:%S'
)

# Загрузка токена
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

if not TOKEN:
    print("❌ ОШИБКА: Токен не найден!")
    exit(1)

# Инициализация базы данных
db = ScheduleDatabase()
print("🤖 Бот с поддержкой подгрупп запущен")

# === КОНСТАНТЫ ===
DAYS_RU = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
DAYS_ORDER = {day.lower(): idx for idx, day in enumerate(DAYS_RU)}
VALID_SUBGROUPS = ['1', '2', 'all']

# === КЭШИРОВАНИЕ ДАННЫХ ===
_schedule_cache = {}
_cache_timestamp = None

# === ХРАНЕНИЕ ВЫБРАННОЙ ПОДГРУППЫ ===
user_subgroups = {}


# === УТИЛИТНЫЕ ФУНКЦИИ ===
def escape_markdown_v2(text: str) -> str:
    """Экранирует специальные символы для MarkdownV2"""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text


def safe_markdown_bold(text: str) -> str:
    """Возвращает текст в жирном начертании с экранированием"""
    return f"*{escape_markdown_v2(text)}*"


def get_cached_schedule(subgroup: str = 'all'):
    """Кэшируем расписание для каждой подгруппы отдельно"""
    global _schedule_cache, _cache_timestamp

    cache_key = f"subgroup_{subgroup}"
    now = datetime.datetime.now()

    if (cache_key not in _schedule_cache or
            _cache_timestamp is None or
            (now - _cache_timestamp).seconds > 300):

        _schedule_cache[cache_key] = {}
        days = db.get_all_days_with_lessons_for_subgroup(subgroup)
        for day in days:
            lessons = db.get_lessons_by_day_and_subgroup(day, subgroup)
            if lessons:
                _schedule_cache[cache_key][day] = lessons
        _cache_timestamp = now
        logging.info(f"Кэш для подгруппы {subgroup} обновлен")

    return _schedule_cache.get(cache_key, {})


def clear_schedule_cache(subgroup: str = None):
    """Очистка кэша"""
    global _schedule_cache, _cache_timestamp
    if subgroup:
        cache_key = f"subgroup_{subgroup}"
        if cache_key in _schedule_cache:
            del _schedule_cache[cache_key]
    else:
        _schedule_cache = {}
    _cache_timestamp = None


def get_user_subgroup(user_id: int) -> str:
    """Получить выбранную подгруппу пользователя"""
    return user_subgroups.get(user_id, '1')


def set_user_subgroup(user_id: int, subgroup: str):
    """Установить подгруппу для пользователя"""
    user_subgroups[user_id] = subgroup
    clear_schedule_cache(subgroup)


def format_subgroup_mark(subgroup: str) -> str:
    """Форматирование обозначения подгруппы"""
    if subgroup == '1':
        return " [1]"
    elif subgroup == '2':
        return " [2]"
    return ""


def format_subgroup_text(subgroup: str) -> str:
    """Форматирование текста подгруппы для списка"""
    if subgroup == 'all':
        return "👥 (для всех)"
    elif subgroup == '1':
        return "1️⃣ (подгруппа 1)"
    elif subgroup == '2':
        return "2️⃣ (подгруппа 2)"
    return f"({subgroup})"


async def get_day_schedule_message(day_ru: str, subgroup: str, day_type: str = "сегодня") -> str:
    """Получить сообщение с расписанием на день"""
    cached_data = get_cached_schedule(subgroup)
    lessons = cached_data.get(day_ru, [])

    if lessons:
        message = f"📅 {safe_markdown_bold(day_ru)} (подгруппа {escape_markdown_v2(subgroup)}):\n\n"
        for lesson in lessons:
            message += f"• {lesson['time']} - {escape_markdown_v2(lesson['subject'])}{format_subgroup_mark(lesson.get('subgroup'))}\n"
    else:
        message = f"🎉 {safe_markdown_bold(day_ru)}\n{day_type.capitalize()} нет уроков для подгруппы {escape_markdown_v2(subgroup)}!"

    return message


# === КОМАНДЫ БОТА ===
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user = update.effective_user
    user_id = user.id
    subgroup = get_user_subgroup(user_id)

    cached_data = get_cached_schedule(subgroup)
    days_with_lessons = list(cached_data.keys())
    week_overview = format_week_overview(days_with_lessons)

    keyboard = create_main_menu(subgroup)

    await update.message.reply_text(
        f"Привет, {escape_markdown_v2(user.first_name)}! 👋\n"
        f"Текущая подгруппа: 🎯 {escape_markdown_v2(subgroup)}\n\n{week_overview}",
        parse_mode='MarkdownV2',
        reply_markup=keyboard
    )


async def subgroup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда выбора подгруппы: /subgroup"""
    user_id = update.effective_user.id
    current_subgroup = get_user_subgroup(user_id)

    keyboard = create_subgroup_selection_keyboard(current_subgroup)
    await update.message.reply_text(
        r"🎯 *Выберите вашу подгруппу:*\n\n"
        r"• Подгруппа 1 - ваши индивидуальные уроки\n"
        r"• Подгруппа 2 - уроки для второй подгруппы\n"
        r"• Для всех - общие уроки",
        parse_mode='MarkdownV2',
        reply_markup=keyboard
    )


async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню выбора дня: /schedule"""
    user_id = update.effective_user.id
    subgroup = get_user_subgroup(user_id)

    keyboard = create_day_selection_keyboard(subgroup)
    await update.message.reply_text(
        f"📅 Выберите день (подгруппа {escape_markdown_v2(subgroup)}):",
        reply_markup=keyboard
    )


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на сегодня: /today"""
    user_id = update.effective_user.id
    subgroup = get_user_subgroup(user_id)

    today_idx = datetime.datetime.now().weekday()
    today_ru = DAYS_RU[today_idx]

    message = await get_day_schedule_message(today_ru, subgroup, "сегодня")
    await update.message.reply_text(message, parse_mode='MarkdownV2')


async def tomorrow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на завтра: /tomorrow"""
    user_id = update.effective_user.id
    subgroup = get_user_subgroup(user_id)

    tomorrow_idx = (datetime.datetime.now().weekday() + 1) % 7
    tomorrow_ru = DAYS_RU[tomorrow_idx]

    message = await get_day_schedule_message(tomorrow_ru, subgroup, "завтра")
    await update.message.reply_text(message, parse_mode='MarkdownV2')


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка inline-кнопок"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # Обработка выбора подгруппы
    if query.data.startswith('subgroup_'):
        subgroup = query.data.replace('subgroup_', '')
        if subgroup in VALID_SUBGROUPS:
            set_user_subgroup(user_id, subgroup)
            keyboard = create_main_menu(subgroup)
            await query.edit_message_text(
                text=f"✅ Выбрана подгруппа: 🎯 {escape_markdown_v2(subgroup)}\n\nТеперь вы будете видеть уроки для этой подгруппы\.",
                parse_mode='MarkdownV2',
                reply_markup=keyboard
            )
        return

    # Обработка кнопок удаления
    if query.data.startswith('confirm_delete_'):
        try:
            lesson_id = int(query.data.split('_')[-1])
            lesson = db.get_lesson_by_id(lesson_id)

            if lesson:
                success = db.delete_lesson(lesson_id)
                if success:
                    clear_schedule_cache()
                    message = r"✅ Урок удален\!\n\n"
                    message += f"• Предмет: {escape_markdown_v2(lesson.get('subject', 'Неизвестно'))}\n"
                    if lesson.get('subgroup') != 'all':
                        message += f"• Подгруппа: {escape_markdown_v2(lesson.get('subgroup'))}\n"
                    message += f"• Время: {escape_markdown_v2(lesson.get('time', 'Неизвестно'))}\n"
                    message += f"• День: {escape_markdown_v2(lesson.get('day', 'Неизвестно'))}"
                else:
                    message = "❌ Ошибка при удалении урока"
            else:
                message = "❌ Урок не найден"

            await query.edit_message_text(text=message, parse_mode='MarkdownV2')
        except (ValueError, IndexError):
            await query.edit_message_text("❌ Ошибка: некорректный ID урока", parse_mode='MarkdownV2')
        return

    # Обработка кнопок выбора дня
    if query.data.startswith('day_'):
        parts = query.data.split('_')
        if len(parts) >= 3:
            day = parts[1]
            subgroup = parts[2] if len(parts) > 2 else get_user_subgroup(user_id)

            cached_data = get_cached_schedule(subgroup)

            if day == 'Вся неделя':
                message = format_full_schedule_by_days(cached_data)
                message += f"\n\n🎯 *Подгруппа: {escape_markdown_v2(subgroup)}*"
            else:
                lessons = cached_data.get(day, [])
                message = format_day_schedule(day, lessons)
                message += f"\n\n🎯 *Подгруппа: {escape_markdown_v2(subgroup)}*"

            await query.edit_message_text(text=message, parse_mode='MarkdownV2')
        return

    # Обработка кнопки смены подгруппы
    if query.data == 'change_subgroup':
        current_subgroup = get_user_subgroup(user_id)
        keyboard = create_subgroup_selection_keyboard(current_subgroup)
        await query.edit_message_text(
            text="🎯 *Выберите подгруппу:*",
            parse_mode='MarkdownV2',
            reply_markup=keyboard
        )
        return

    # Обработка кнопки отмены
    if query.data in ['cancel_delete', 'cancel', 'cancel_subgroup']:
        await query.edit_message_text(
            text="❌ Действие отменено",
            parse_mode='MarkdownV2'
        )


async def add_lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавить урок: /add <предмет> <время> <день> [подгруппа]"""
    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            r"📝 *Формат:* `/add <предмет> <время> <день> \[подгруппа\]`\n\n"
            r"📌 *Примеры:*\n"
            r"• `/add Математика 10:00 Понедельник` \- для всех\n"
            r"• `/add Математика 10:00 Понедельник 1` \- для подгруппы 1\n"
            r"• `/add Математика 10:00 Понедельник 2` \- для подгруппы 2\n"
            r"• `/add Математика 10:00 Понедельник all` \- для всех подгрупп\n\n"
            r"⚠️ *Подгруппа по умолчанию:* `all`",
            parse_mode='MarkdownV2'
        )
        return

    subject, time, day = context.args[0], context.args[1], context.args[2]
    subgroup = context.args[3] if len(context.args) > 3 else 'all'

    if subgroup not in VALID_SUBGROUPS:
        await update.message.reply_text(
            r"❌ Некорректная подгруппа\. Используйте: `1`, `2` или `all`",
            parse_mode='MarkdownV2'
        )
        return

    lesson_data = {
        'subject': subject,
        'time': time,
        'day': day,
        'subgroup': subgroup
    }

    result = db.add_lesson(lesson_data)

    if result.get('success'):
        clear_schedule_cache(subgroup)
        subgroup_text = f" (подгруппа {subgroup})" if subgroup != 'all' else " (для всех)"
        await update.message.reply_text(f"✅ '{subject}' добавлен на {day} в {time}{subgroup_text}")
    else:
        await update.message.reply_text("❌ Ошибка при добавлении урока")


async def delete_lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удалить урок: /delete <id>"""
    if not context.args:
        await update.message.reply_text("Укажите ID урока: `/delete 1`", parse_mode='MarkdownV2')
        return

    try:
        lesson_id = int(context.args[0])
        lesson = db.get_lesson_by_id(lesson_id)

        if not lesson:
            await update.message.reply_text("❌ Урок не найден")
            return

        keyboard = create_confirmation_keyboard(lesson_id)
        message = r"🗑️ *Удалить урок?*\n\n"
        message += f"• Предмет: {escape_markdown_v2(lesson.get('subject', 'Неизвестно'))}\n"
        message += f"• Время: {escape_markdown_v2(lesson.get('time', 'Неизвестно'))}\n"
        message += f"• День: {escape_markdown_v2(lesson.get('day', 'Неизвестно'))}\n"
        if lesson.get('subgroup') != 'all':
            message += f"• Подгруппа: {escape_markdown_v2(lesson.get('subgroup'))}\n"
        message += f"• ID: {escape_markdown_v2(str(lesson.get('id', 'Неизвестно')))}"

        await update.message.reply_text(
            message,
            parse_mode='MarkdownV2',
            reply_markup=keyboard
        )
    except ValueError:
        await update.message.reply_text(r"❌ Введите правильный ID \(число\)", parse_mode='MarkdownV2')


async def week_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на всю неделю: /week"""
    user_id = update.effective_user.id
    subgroup = get_user_subgroup(user_id)

    cached_data = get_cached_schedule(subgroup)
    message = format_full_schedule_by_days(cached_data)
    message += f"\n\n🎯 *Подгруппа: {escape_markdown_v2(subgroup)}*"

    await update.message.reply_text(message, parse_mode='MarkdownV2')


async def all_lessons_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вывод всех уроков подряд: /all"""
    try:
        # Получаем все уроки из базы
        all_lessons = db.get_all_lessons()

        if not all_lessons:
            await update.message.reply_text("📭 В базе данных нет уроков")
            return

        # Сортируем уроки по дню и времени
        def sort_key(lesson):
            day = lesson.get('day', '').lower()
            time_str = lesson.get('time', '00:00')
            return (DAYS_ORDER.get(day, 99), datetime.datetime.strptime(time_str, '%H:%M').time() if ':' in time_str else datetime.time(0, 0))

        all_lessons.sort(key=sort_key)

        # Формируем сообщение
        result = "📚 *Все уроки в базе данных:*\n\n"
        current_day = None

        for lesson in all_lessons:
            day = lesson.get('day', 'Неизвестно')
            time = lesson.get('time', '??:??')
            subject = lesson.get('subject', 'Неизвестно')
            subgroup = lesson.get('subgroup', 'all')

            if day != current_day:
                result += f"\n{safe_markdown_bold(day.upper())}\n"
                current_day = day

            result += f"🕒 {escape_markdown_v2(time)} \- {escape_markdown_v2(subject)} {format_subgroup_text(subgroup)}\n"

        result += f"\n📊 Всего уроков в базе: {safe_markdown_bold(str(len(all_lessons)))}"
        await update.message.reply_text(result, parse_mode='MarkdownV2')

    except AttributeError as e:
        logging.error(f"Ошибка в all_lessons_command: {e}")
        await update.message.reply_text(
            r"❌ Ошибка: метод get\_all\_lessons\(\) не найден в базе данных\.\n"
            r"Проверьте файл database\.py",
            parse_mode='MarkdownV2'
        )
    except Exception as e:
        logging.error(f"Ошибка в all_lessons_command: {e}")
        await update.message.reply_text(f"❌ Ошибка при получении уроков: {escape_markdown_v2(str(e))}", parse_mode='MarkdownV2')


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь: /help"""
    help_text = (
        r"🆘 *Справка по командам с поддержкой подгрупп*\n\n"
        r"🎯 *Работа с подгруппами:*\n"
        r"/subgroup \- Выбрать подгруппу \(1, 2 или all\)\n"
        r"🔄 Подгруппа сохраняется для каждого пользователя отдельно\n\n"
        r"📅 *Просмотр расписания \(для выбранной подгруппы\):*\n"
        r"/schedule \- Выбрать день недели\n"
        r"/today \- Расписание на сегодня\n"
        r"/tomorrow \- Расписание на завтра\n"
        r"/week \- Вся неделя\n"
        r"/all \- Все уроки в базе\n\n"
        r"➕ *Добавление урока \(с указанием подгруппы\):*\n"
        r"`/add <предмет> <время> <день> \[подгруппа\]`\n\n"
        r"*Примеры:*\n"
        r"• `/add Математика 10:00 Понедельник` \- для всех\n"
        r"• `/add Математика 10:00 Понедельник 1` \- для подгруппы 1\n"
        r"• `/add Математика 10:00 Понедельник 2` \- для подгруппы 2\n"
        r"• `/add Математика 10:00 Понедельник all` \- для всех подгрупп\n\n"
        r"🗑️ *Удаление:*\n"
        r"/delete <ID\_урока> \- Удалить урок\n\n"
        r"💡 *Советы:*\n"
        r"• Используйте кнопки для быстрого доступа\n"
        r"• ID урока можно увидеть в расписании\n"
        r"• Подгруппа: 1, 2 или all \(для всех\)\n"
        r"• Дни: Понедельник\-Воскресенье"
    )
    await update.message.reply_text(help_text, parse_mode='MarkdownV2')


async def clear_cache_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очистка кэша: /clearcache"""
    clear_schedule_cache()
    await update.message.reply_text("✅ Кэш расписания очищен", parse_mode='MarkdownV2')


def main():
    """Запуск бота"""
    print("🚀 Запуск бота с поддержкой подгрупп...")
    print(f"📱 Токен: {TOKEN[:10]}...")

    db.migrate_to_subgroups()
    print("✅ База данных обновлена для поддержки подгрупп")

    application = Application.builder().token(TOKEN).build()

    # Регистрация команд
    commands = [
        ("start", start_command),
        ("subgroup", subgroup_command),
        ("today", today_command),
        ("tomorrow", tomorrow_command),
        ("schedule", schedule_command),
        ("week", week_command),
        ("all", all_lessons_command),
        ("help", help_command),
        ("add", add_lesson_command),
        ("delete", delete_lesson_command),
        ("clearcache", clear_cache_command),
    ]

    for command, handler in commands:
        application.add_handler(CommandHandler(command, handler))

    # Обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_callback))

    print("⚡ Функции:")
    print("  • Поддержка 2 подгрупп и общих уроков")
    print("  • Кэширование для каждой подгруппы отдельно")
    print("  • Персональные настройки подгруппы для каждого пользователя")
    print("  • Вывод всех уроков командой /all")
    print("\n📝 Напишите /start в Telegram")
    print("🎯 Используйте /subgroup для выбора подгруппы")

    try:
        application.run_polling(
            poll_interval=2.0,
            timeout=15,
            drop_pending_updates=True,
            close_loop=False
        )
    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")


if __name__ == "__main__":
    main()