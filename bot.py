import os
import datetime
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
from database import ScheduleDatabase
from keyboards import create_main_menu, get_days_list, get_subgroups_list
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
DAYS_COMMANDS = {
    'понедельник': 'Понедельник',
    'вторник': 'Вторник',
    'среда': 'Среда',
    'четверг': 'Четверг',
    'пятница': 'Пятница',
    'суббота': 'Суббота',
    'воскресенье': 'Воскресенье'
}
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


def format_subgroup_text(subgroup: str) -> str:
    """Форматирование текста подгруппы для списка"""
    if subgroup == 'all':
        return "👥 (для всех)"
    elif subgroup == '1':
        return "1️⃣ (подгруппа 1)"
    elif subgroup == '2':
        return "2️⃣ (подгруппа 2)"
    return f"({subgroup})"


# === КОМАНДЫ БОТА ===
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    try:
        user = update.effective_user
        user_id = user.id
        subgroup = get_user_subgroup(user_id)

        cached_data = get_cached_schedule(subgroup)
        days_with_lessons = list(cached_data.keys())
        week_overview = format_week_overview(days_with_lessons)

        keyboard = create_main_menu(subgroup)

        await update.message.reply_text(
            f"Привет, {escape_markdown_v2(user.first_name)}\\! 👋\n"
            f"Текущая подгруппа: 🎯 {escape_markdown_v2(subgroup)}\n\n{week_overview}",
            parse_mode='MarkdownV2',
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"❌ ОШИБКА в start_command: {e}")
        import traceback
        traceback.print_exc()
        if update and update.message:
            await update.message.reply_text(f"❌ Ошибка при запуске: {str(e)[:100]}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь: /help - показывает все команды"""
    help_text = (
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
    await update.message.reply_text(help_text, parse_mode='MarkdownV2')


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на сегодня: /today"""
    try:
        user_id = update.effective_user.id
        subgroup = get_user_subgroup(user_id)

        today_idx = datetime.datetime.now().weekday()
        today_ru = DAYS_RU[today_idx]

        cached_data = get_cached_schedule(subgroup)
        lessons = cached_data.get(today_ru, [])

        if lessons:
            message = f"📅 {safe_markdown_bold(today_ru)} (подгруппа {escape_markdown_v2(subgroup)}):\n\n"
            for lesson in lessons:
                message += f"• {lesson['time']} - {escape_markdown_v2(lesson['subject'])}\n"
        else:
            message = f"🎉 {safe_markdown_bold(today_ru)}\nСегодня нет уроков для подгруппы {escape_markdown_v2(subgroup)}!"

        await update.message.reply_text(message, parse_mode='MarkdownV2')
    except Exception as e:
        print(f"❌ ОШИБКА в today_command: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")


async def tomorrow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на завтра: /tomorrow"""
    try:
        user_id = update.effective_user.id
        subgroup = get_user_subgroup(user_id)

        tomorrow_idx = (datetime.datetime.now().weekday() + 1) % 7
        tomorrow_ru = DAYS_RU[tomorrow_idx]

        cached_data = get_cached_schedule(subgroup)
        lessons = cached_data.get(tomorrow_ru, [])

        if lessons:
            message = f"📅 {safe_markdown_bold(tomorrow_ru)} (подгруппа {escape_markdown_v2(subgroup)}):\n\n"
            for lesson in lessons:
                message += f"• {lesson['time']} - {escape_markdown_v2(lesson['subject'])}\n"
        else:
            message = f"🎉 {safe_markdown_bold(tomorrow_ru)}\nЗавтра нет уроков для подгруппы {escape_markdown_v2(subgroup)}!"

        await update.message.reply_text(message, parse_mode='MarkdownV2')
    except Exception as e:
        print(f"❌ ОШИБКА в tomorrow_command: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")


async def week_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на всю неделю: /week"""
    try:
        user_id = update.effective_user.id
        subgroup = get_user_subgroup(user_id)

        cached_data = get_cached_schedule(subgroup)
        message = format_full_schedule_by_days(cached_data)
        message += f"\n\n🎯 *Подгруппа: {escape_markdown_v2(subgroup)}*"

        await update.message.reply_text(message, parse_mode='MarkdownV2')
    except Exception as e:
        print(f"❌ ОШИБКА в week_command: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")


async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список дней: /schedule"""
    try:
        user_id = update.effective_user.id
        subgroup = get_user_subgroup(user_id)

        days_list = get_days_list(subgroup)
        await update.message.reply_text(
            days_list,
            parse_mode='MarkdownV2'
        )
    except Exception as e:
        print(f"❌ ОШИБКА в schedule_command: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")


async def subgroup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список подгрупп: /subgroup"""
    try:
        subgroups_list = get_subgroups_list()
        await update.message.reply_text(
            subgroups_list,
            parse_mode='MarkdownV2'
        )
    except Exception as e:
        print(f"❌ ОШИБКА в subgroup_command: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")


# === КОМАНДЫ ДЛЯ ДНЕЙ ===
async def day_monday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на понедельник: /day_понедельник"""
    await handle_day_command(update, context, "Понедельник")


async def day_tuesday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на вторник: /day_вторник"""
    await handle_day_command(update, context, "Вторник")


async def day_wednesday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на среду: /day_среда"""
    await handle_day_command(update, context, "Среда")


async def day_thursday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на четверг: /day_четверг"""
    await handle_day_command(update, context, "Четверг")


async def day_friday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на пятницу: /day_пятница"""
    await handle_day_command(update, context, "Пятница")


async def day_saturday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на субботу: /day_суббота"""
    await handle_day_command(update, context, "Суббота")


async def day_sunday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на воскресенье: /day_воскресенье"""
    await handle_day_command(update, context, "Воскресенье")


async def handle_day_command(update: Update, context: ContextTypes.DEFAULT_TYPE, day: str):
    """Обработчик команд для дней"""
    try:
        user_id = update.effective_user.id
        subgroup = get_user_subgroup(user_id)

        cached_data = get_cached_schedule(subgroup)
        lessons = cached_data.get(day, [])

        if lessons:
            message = f"📅 {safe_markdown_bold(day)} (подгруппа {escape_markdown_v2(subgroup)}):\n\n"
            for lesson in lessons:
                message += f"• {lesson['time']} - {escape_markdown_v2(lesson['subject'])}\n"
        else:
            message = f"🎉 {safe_markdown_bold(day)}\nНет уроков для подгруппы {escape_markdown_v2(subgroup)}!"

        await update.message.reply_text(message, parse_mode='MarkdownV2')

    except Exception as e:
        print(f"❌ Ошибка в команде дня {day}: {e}")
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")


# === КОМАНДЫ ПОДГРУПП ===
async def subgroup_1_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор подгруппы 1: /subgroup_1"""
    await handle_subgroup_command(update, context, '1')


async def subgroup_2_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор подгруппы 2: /subgroup_2"""
    await handle_subgroup_command(update, context, '2')


async def subgroup_all_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Выбор 'для всех' подгрупп: /subgroup_all"""
    await handle_subgroup_command(update, context, 'all')


async def handle_subgroup_command(update: Update, context: ContextTypes.DEFAULT_TYPE, subgroup: str):
    """Обработчик команд подгрупп"""
    try:
        user_id = update.effective_user.id
        set_user_subgroup(user_id, subgroup)
        keyboard = create_main_menu(subgroup)

        await update.message.reply_text(
            f"✅ Выбрана подгруппа: 🎯 {escape_markdown_v2(subgroup)}",
            parse_mode='MarkdownV2',
            reply_markup=keyboard
        )

    except Exception as e:
        print(f"❌ Ошибка в команде подгруппы {subgroup}: {e}")
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")


# === КОМАНДЫ ДЛЯ РАБОТЫ С УРОКАМИ ===
async def add_lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавить урок: /add <предмет> <время> <день> [подгруппа]"""
    try:
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
    except Exception as e:
        print(f"❌ ОШИБКА в add_lesson_command: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")


async def delete_lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удалить урок: /delete <id>"""
    try:
        if not context.args:
            await update.message.reply_text("Укажите ID урока: `/delete 1`", parse_mode='MarkdownV2')
            return

        try:
            lesson_id = int(context.args[0])
            lesson = db.get_lesson_by_id(lesson_id)

            if not lesson:
                await update.message.reply_text("❌ Урок не найден")
                return

            message = r"🗑️ *Удалить урок?*\n\n"
            message += f"• Предмет: {escape_markdown_v2(lesson.get('subject', 'Неизвестно'))}\n"
            message += f"• Время: {escape_markdown_v2(lesson.get('time', 'Неизвестно'))}\n"
            message += f"• День: {escape_markdown_v2(lesson.get('day', 'Неизвестно'))}\n"
            if lesson.get('subgroup') != 'all':
                message += f"• Подгруппа: {escape_markdown_v2(lesson.get('subgroup'))}\n"
            message += f"• ID: {escape_markdown_v2(str(lesson.get('id', 'Неизвестно')))}\n\n"
            message += f"📝 *Для подтверждения напишите:*\n"
            message += f"`/confirm_delete_{lesson_id}` - удалить\n"
            message += "`/cancel` - отменить"

            await update.message.reply_text(message, parse_mode='MarkdownV2')
        except ValueError:
            await update.message.reply_text(r"❌ Введите правильный ID \(число\)", parse_mode='MarkdownV2')
    except Exception as e:
        print(f"❌ ОШИБКА в delete_lesson_command: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")


async def confirm_delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Подтверждение удаления: /confirm_delete_<id>"""
    try:
        command = update.message.text
        if command.startswith('/confirm_delete_'):
            lesson_id = int(command.replace('/confirm_delete_', ''))

            lesson = db.get_lesson_by_id(lesson_id)
            if lesson:
                success = db.delete_lesson(lesson_id)
                if success:
                    clear_schedule_cache()
                    await update.message.reply_text(f"✅ Урок #{lesson_id} удален")
                else:
                    await update.message.reply_text("❌ Ошибка при удалении")
            else:
                await update.message.reply_text("❌ Урок не найден")

    except Exception as e:
        print(f"❌ Ошибка в подтверждении удаления: {e}")
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")


async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отмена действия: /cancel"""
    await update.message.reply_text("❌ Действие отменено")


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
            return (DAYS_ORDER.get(day, 99),
                    datetime.datetime.strptime(time_str, '%H:%M').time() if ':' in time_str else datetime.time(0, 0))

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
        await update.message.reply_text(f"❌ Ошибка при получении уроков: {escape_markdown_v2(str(e))}",
                                        parse_mode='MarkdownV2')


async def clear_cache_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очистка кэша: /clearcache"""
    try:
        clear_schedule_cache()
        await update.message.reply_text("✅ Кэш расписания очищен", parse_mode='MarkdownV2')
    except Exception as e:
        print(f"❌ ОШИБКА в clear_cache_command: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")


# === ОБРАБОТЧИК ДЛЯ ДИНАМИЧЕСКИХ КОМАНД ===
async def dynamic_day_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик для /day_<день>"""
    try:
        command = update.message.text.lower().replace('/', '')

        if command.startswith('day_'):
            day_key = command.replace('day_', '')
            if day_key in DAYS_COMMANDS:
                await handle_day_command(update, context, DAYS_COMMANDS[day_key])
            else:
                await update.message.reply_text(f"❌ Неизвестный день: {day_key}")

    except Exception as e:
        print(f"❌ Ошибка в динамической команде дня: {e}")
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")


def main():
    """Запуск бота"""
    try:
        print("🚀 Запуск бота с поддержкой подгрупп...")
        print(f"📱 Токен: {TOKEN[:10]}...")

        db.migrate_to_subgroups()
        print("✅ База данных обновлена для поддержки подгрупп")

        application = Application.builder().token(TOKEN).build()

        # === ГЛОБАЛЬНЫЙ ОБРАБОТЧИК ОШИБОК ===
        async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            try:
                print(f"🔥 Глобальная ошибка: {context.error}")
                import traceback
                traceback.print_exc()

                if update and update.effective_message:
                    await update.effective_message.reply_text(
                        "❌ Произошла ошибка. Разработчик уже уведомлен."
                    )
            except:
                pass

        application.add_error_handler(error_handler)

        # Регистрация ОСНОВНЫХ команд
        basic_commands = [
            ("start", start_command),
            ("help", help_command),
            ("today", today_command),
            ("tomorrow", tomorrow_command),
            ("week", week_command),
            ("schedule", schedule_command),
            ("subgroup", subgroup_command),
            ("all", all_lessons_command),
            ("add", add_lesson_command),
            ("delete", delete_lesson_command),
            ("clearcache", clear_cache_command),
            ("cancel", cancel_command),
        ]

        # Регистрация команд ДНЕЙ
        day_commands = [
            ("day_понедельник", day_monday_command),
            ("day_вторник", day_tuesday_command),
            ("day_среда", day_wednesday_command),
            ("day_четверг", day_thursday_command),
            ("day_пятница", day_friday_command),
            ("day_суббота", day_saturday_command),
            ("day_воскресенье", day_sunday_command),
        ]

        # Регистрация команд ПОДГРУПП
        subgroup_commands = [
            ("subgroup_1", subgroup_1_command),
            ("subgroup_2", subgroup_2_command),
            ("subgroup_all", subgroup_all_command),
        ]

        # Регистрируем все статические команды
        all_commands = basic_commands + day_commands + subgroup_commands
        for command, handler in all_commands:
            application.add_handler(CommandHandler("day_nohenenbHhwmk", handler))

        # Регистрируем динамические команды (confirm_delete_*)
        application.add_handler(MessageHandler(
            filters.Regex(r'^/confirm_delete_\d+$'),
            confirm_delete_command
        ))

        print("✅ Бот настроен со следующими командами:")
        for cmd, _ in all_commands:
            print(f"   • /{cmd}")
        print("\n📝 Напишите /start в Telegram")
        print("❓ Напишите /help для списка всех команд")

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
    except Exception as e:
        print(f"❌ Критическая ошибка при запуске бота: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()