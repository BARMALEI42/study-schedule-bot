import os
import datetime
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
from dotenv import load_dotenv
from database import ScheduleDatabase
from keyboards import create_main_menu, create_confirmation_keyboard, create_day_selection_keyboard, \
    create_subgroup_selection_keyboard
from messages import (
    WELCOME_MESSAGE, HELP_MESSAGE,
    format_lesson_message,
    format_day_schedule, format_full_schedule_by_days, format_week_overview
)

# === ОПТИМИЗАЦИЯ НАСТРОЕК ЛОГГИРОВАНИЯ ===
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.WARNING,
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

# === КЭШИРОВАНИЕ ДАННЫХ С ПОДДЕРЖКОЙ ПОДГРУПП ===
_schedule_cache = {}
_cache_timestamp = None
CACHE_TIMEOUT = 300


def get_cached_schedule(subgroup: str = 'all'):
    """Кэшируем расписание для каждой подгруппы отдельно"""
    global _schedule_cache, _cache_timestamp

    cache_key = f"subgroup_{subgroup}"
    now = datetime.datetime.now()

    if (cache_key not in _schedule_cache or
            _cache_timestamp is None or
            (now - _cache_timestamp).seconds > CACHE_TIMEOUT):

        # Обновляем кэш для этой подгруппы
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


# === ХРАНЕНИЕ ВЫБРАННОЙ ПОДГРУППЫ ДЛЯ КАЖДОГО ПОЛЬЗОВАТЕЛЯ ===
user_subgroups = {}


def get_user_subgroup(user_id: int) -> str:
    """Получить выбранную подгруппу пользователя"""
    return user_subgroups.get(user_id, '1')  # По умолчанию подгруппа 1


def set_user_subgroup(user_id: int, subgroup: str):
    """Установить подгруппу для пользователя"""
    user_subgroups[user_id] = subgroup
    clear_schedule_cache(subgroup)  # Очищаем кэш для этой подгруппы


# === КОМАНДЫ БОТА ===
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user = update.effective_user
    user_id = user.id
    subgroup = get_user_subgroup(user_id)

    # Используем кэшированные данные для подгруппы пользователя
    cached_data = get_cached_schedule(subgroup)
    days_with_lessons = list(cached_data.keys())
    week_overview = format_week_overview(days_with_lessons)

    keyboard = create_main_menu(subgroup)

    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n"
        f"Текущая подгруппа: 🎯 {subgroup}\n\n{week_overview}",
        parse_mode='Markdown',
        reply_markup=keyboard
    )


async def subgroup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда выбора подгруппы: /subgroup"""
    user_id = update.effective_user.id
    current_subgroup = get_user_subgroup(user_id)

    keyboard = create_subgroup_selection_keyboard(current_subgroup)
    await update.message.reply_text(
        "🎯 *Выберите вашу подгруппу:*\n\n"
        "• Подгруппа 1 - ваши индивидуальные уроки\n"
        "• Подгруппа 2 - уроки для второй подгруппы\n"
        "• Для всех - общие уроки",
        parse_mode='Markdown',
        reply_markup=keyboard
    )


async def schedule_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Меню выбора дня: /schedule"""
    user_id = update.effective_user.id
    subgroup = get_user_subgroup(user_id)

    keyboard = create_day_selection_keyboard(subgroup)
    await update.message.reply_text(
        f"📅 Выберите день (подгруппа {subgroup}):",
        reply_markup=keyboard
    )


async def today_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на сегодня: /today"""
    user_id = update.effective_user.id
    subgroup = get_user_subgroup(user_id)

    days_ru = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    today_idx = datetime.datetime.now().weekday()
    today_ru = days_ru[today_idx]

    # Используем кэш для подгруппы
    cached_data = get_cached_schedule(subgroup)
    lessons = cached_data.get(today_ru, [])

    if lessons:
        message = f"📅 *{today_ru}* (подгруппа {subgroup}):\n\n"
        for lesson in lessons:
            subgroup_mark = ""
            if lesson.get('subgroup') == '1':
                subgroup_mark = " [1]"
            elif lesson.get('subgroup') == '2':
                subgroup_mark = " [2]"
            message += f"• {lesson['time']} - {lesson['subject']}{subgroup_mark}\n"
    else:
        message = f"🎉 *{today_ru}*\nСегодня нет уроков для подгруппы {subgroup}!"

    await update.message.reply_text(message, parse_mode='Markdown')


async def tomorrow_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на завтра: /tomorrow"""
    user_id = update.effective_user.id
    subgroup = get_user_subgroup(user_id)

    days_ru = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    tomorrow_idx = (datetime.datetime.now().weekday() + 1) % 7
    tomorrow_ru = days_ru[tomorrow_idx]

    # Используем кэш для подгруппы
    cached_data = get_cached_schedule(subgroup)
    lessons = cached_data.get(tomorrow_ru, [])

    if lessons:
        message = f"📅 *{tomorrow_ru}* (подгруппа {subgroup}):\n\n"
        for lesson in lessons:
            subgroup_mark = ""
            if lesson.get('subgroup') == '1':
                subgroup_mark = " [1]"
            elif lesson.get('subgroup') == '2':
                subgroup_mark = " [2]"
            message += f"• {lesson['time']} - {lesson['subject']}{subgroup_mark}\n"
    else:
        message = f"📅 *{tomorrow_ru}*\nЗавтра нет уроков для подгруппы {subgroup}!"

    await update.message.reply_text(message, parse_mode='Markdown')


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка inline-кнопок"""
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    # === ОБРАБОТКА ВЫБОРА ПОДГРУППЫ ===
    if query.data.startswith('subgroup_'):
        subgroup = query.data.replace('subgroup_', '')
        if subgroup in ['1', '2', 'all']:
            set_user_subgroup(user_id, subgroup)
            keyboard = create_main_menu(subgroup)
            await query.edit_message_text(
                text=f"✅ Выбрана подгруппа: 🎯 {subgroup}\n\nТеперь вы будете видеть уроки для этой подгруппы.",
                parse_mode='Markdown',
                reply_markup=keyboard
            )
        return

    # === ОБРАБОТКА КНОПОК УДАЛЕНИЯ ===
    if query.data.startswith('confirm_delete_'):
        try:
            lesson_id = int(query.data.split('_')[-1])
            lesson = db.get_lesson_by_id(lesson_id)

            if lesson:
                success = db.delete_lesson(lesson_id)
                if success:
                    clear_schedule_cache()  # Очищаем весь кэш
                    message = f"✅ Урок удален!\n\n"
                    message += f"• Предмет: {lesson.get('subject', 'Неизвестно')}\n"
                    if lesson.get('subgroup') != 'all':
                        message += f"• Подгруппа: {lesson.get('subgroup')}\n"
                    message += f"• Время: {lesson.get('time', 'Неизвестно')}\n"
                    message += f"• День: {lesson.get('day', 'Неизвестно')}"
                else:
                    message = "❌ Ошибка при удалении урока"
            else:
                message = "❌ Урок не найден"

        except (ValueError, IndexError):
            message = "❌ Ошибка: некорректный ID урока"

        await query.edit_message_text(text=message, parse_mode='Markdown')

    # === ОБРАБОТКА КНОПОК ВЫБОРА ДНЯ С ПОДГРУППОЙ ===
    elif query.data.startswith('day_'):
        parts = query.data.split('_')
        if len(parts) >= 3:
            day = parts[1]
            subgroup = parts[2] if len(parts) > 2 else get_user_subgroup(user_id)

            cached_data = get_cached_schedule(subgroup)

            if day == 'Вся неделя':
                message = format_full_schedule_by_days(cached_data)
                message += f"\n\n🎯 *Подгруппа: {subgroup}*"
            else:
                lessons = cached_data.get(day, [])
                message = format_day_schedule(day, lessons)
                message += f"\n\n🎯 *Подгруппа: {subgroup}*"

            await query.edit_message_text(text=message, parse_mode='Markdown')

    # === ОБРАБОТКА КНОПКИ СМЕНЫ ПОДГРУППЫ ===
    elif query.data == 'change_subgroup':
        current_subgroup = get_user_subgroup(user_id)
        keyboard = create_subgroup_selection_keyboard(current_subgroup)
        await query.edit_message_text(
            text="🎯 *Выберите подгруппу:*",
            parse_mode='Markdown',
            reply_markup=keyboard
        )

    # === ОБРАБОТКА КНОПКИ ОТМЕНЫ ===
    elif query.data in ['cancel_delete', 'cancel', 'cancel_subgroup']:
        await query.edit_message_text(
            text="❌ Действие отменено",
            parse_mode='Markdown'
        )


async def add_lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавить урок: /add <предмет> <время> <день> [подгруппа]"""
    if not context.args or len(context.args) < 3:
        await update.message.reply_text(
            "📝 *Формат:* `/add <предмет> <время> <день> [подгруппа]`\n\n"
            "📌 *Примеры:*\n"
            "• `/add Математика 10:00 Понедельник` - для всех\n"
            "• `/add Математика 10:00 Понедельник 1` - для подгруппы 1\n"
            "• `/add Математика 10:00 Понедельник 2` - для подгруппы 2\n"
            "• `/add Математика 10:00 Понедельник all` - для всех подгрупп\n\n"
            "⚠️ *Подгруппа по умолчанию:* `all`",
            parse_mode='Markdown'
        )
        return

    subject, time, day = context.args[0], context.args[1], context.args[2]
    subgroup = context.args[3] if len(context.args) > 3 else 'all'

    # Проверяем корректность подгруппы
    if subgroup not in ['1', '2', 'all']:
        await update.message.reply_text(
            "❌ Некорректная подгруппа. Используйте: `1`, `2` или `all`",
            parse_mode='Markdown'
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
        clear_schedule_cache(subgroup)  # Очищаем кэш для этой подгруппы
        subgroup_text = f" (подгруппа {subgroup})" if subgroup != 'all' else " (для всех)"
        await update.message.reply_text(f"✅ '{subject}' добавлен на {day} в {time}{subgroup_text}")
    else:
        await update.message.reply_text("❌ Ошибка при добавлении урока")


async def delete_lesson_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Удалить урок: /delete <id>"""
    if not context.args:
        await update.message.reply_text("Укажите ID урока: `/delete 1`", parse_mode='Markdown')
        return

    try:
        lesson_id = int(context.args[0])
        lesson = db.get_lesson_by_id(lesson_id)

        if not lesson:
            await update.message.reply_text("❌ Урок не найден")
            return

        keyboard = create_confirmation_keyboard(lesson_id)
        message = f"🗑️ *Удалить урок?*\n\n"
        message += f"• Предмет: {lesson.get('subject', 'Неизвестно')}\n"
        message += f"• Время: {lesson.get('time', 'Неизвестно')}\n"
        message += f"• День: {lesson.get('day', 'Неизвестно')}\n"
        if lesson.get('subgroup') != 'all':
            message += f"• Подгруппа: {lesson.get('subgroup')}\n"
        message += f"• ID: {lesson.get('id', 'Неизвестно')}"

        await update.message.reply_text(
            message,
            parse_mode='Markdown',
            reply_markup=keyboard
        )
    except ValueError:
        await update.message.reply_text("❌ Введите правильный ID (число)")


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика: /stats"""
    user_id = update.effective_user.id
    subgroup = get_user_subgroup(user_id)

    stats = db.get_stats_for_subgroup(subgroup)

    message = f"📊 *Статистика (подгруппа {subgroup}):*\n\n"
    message += f"• Всего уроков: *{stats['total_lessons']}*\n"
    message += f"• Дней с уроками: *{stats['days_with_lessons']}*\n"
    message += f"• Разных предметов: *{stats['subjects_count']}*\n"

    if stats.get('most_busy_day'):
        message += f"• Самый загруженный день: *{stats['most_busy_day']}*\n"

    # Показываем количество уроков по дням
    if stats.get('lessons_by_day'):
        message += f"\n📅 *Уроков по дням:*\n"
        for day, count in stats['lessons_by_day'].items():
            message += f"• {day}: {count}\n"

    await update.message.reply_text(message, parse_mode='Markdown')


async def week_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на всю неделю: /week"""
    user_id = update.effective_user.id
    subgroup = get_user_subgroup(user_id)

    cached_data = get_cached_schedule(subgroup)
    message = format_full_schedule_by_days(cached_data)
    message += f"\n\n🎯 *Подгруппа: {subgroup}*"

    await update.message.reply_text(message, parse_mode='Markdown')


async def all_lessons_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Вывод всех уроков подряд: /all или /все"""
    try:
        user_id = update.effective_user.id

        # Получаем все уроки из БД
        all_lessons = db.get_all_lessons()

        if not all_lessons:
            await update.message.reply_text("📭 В базе данных нет уроков")
            return

        # Сортируем уроки по дню и времени
        days_order = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
        all_lessons.sort(key=lambda x: (
            days_order.index(x["day"]) if x["day"] in days_order else 999,
            x["time"]
        ))

        # Формируем текст
        result = "📚 *Все уроки в базе данных:*\n\n"
        current_day = None

        for lesson in all_lessons:
            # Определяем подгруппу
            subgroup = lesson.get('subgroup', 'all')
            if subgroup == 'all':
                subgroup_text = "👥 (для всех)"
            elif subgroup == '1':
                subgroup_text = "1️⃣ (подгруппа 1)"
            elif subgroup == '2':
                subgroup_text = "2️⃣ (подгруппа 2)"
            else:
                subgroup_text = f"({subgroup})"

            # Добавляем заголовок дня, если он изменился
            if lesson['day'] != current_day:
                result += f"\n*{lesson['day'].upper()}*\n"
                current_day = lesson['day']

            # Добавляем урок
            result += f"🕒 {lesson['time']} - {lesson['subject']} {subgroup_text}\n"

        # Добавляем статистику
        result += f"\n📊 Всего уроков в базе: *{len(all_lessons)}*"

        await update.message.reply_text(result, parse_mode='Markdown')

    except Exception as e:
        logging.error(f"Ошибка в all_lessons_command: {e}")
        await update.message.reply_text(f"❌ Ошибка при получении уроков: {str(e)}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Помощь: /help"""
    help_text = (
            HELP_MESSAGE +
            "\n\n🎯 *Работа с подгруппами:*\n"
            "• Используйте команду `/subgroup` для выбора подгруппы\n"
            "• Подгруппа `1` - ваши индивидуальные уроки\n"
            "• Подгруппа `2` - уроки для второй подгруппы\n"
            "• `all` - общие уроки для всех\n\n"
            "📝 *Добавление урока с подгруппой:*\n"
            "`/add Математика 10:00 Понедельник 1` - для подгруппы 1\n"
            "`/add Математика 10:00 Понедельник 2` - для подгруппы 2\n"
            "`/add Математика 10:00 Понедельник all` - для всех\n\n"
            "📊 *Просмотр статистики:* `/stats`\n"
            "📅 *Вся неделя:* `/week`"
    )
    await update.message.reply_text(help_text)


async def clear_cache_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очистка кэша: /clearcache"""
    clear_schedule_cache()
    await update.message.reply_text("✅ Кэш расписания очищен")


def main():
    """Запуск бота с поддержкой подгрупп"""
    print("🚀 Запуск бота с поддержкой подгрупп...")
    print(f"📱 Токен: {TOKEN[:10]}...")

    # Миграция старых данных (если нужно)
    db.migrate_to_subgroups()
    print("✅ База данных обновлена для поддержки подгрупп")

    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики команд
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("subgroup", subgroup_command))
    application.add_handler(CommandHandler("today", today_command))
    application.add_handler(CommandHandler("tomorrow", tomorrow_command))
    application.add_handler(CommandHandler("schedule", schedule_command))
    application.add_handler(CommandHandler("week", week_command))
    application.add_handler(CommandHandler("all", all_lessons_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add", add_lesson_command))
    application.add_handler(CommandHandler("delete", delete_lesson_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("clearcache", clear_cache_command))

    # Обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_callback))

    print("⚡ Функции:")
    print("  • Поддержка 2 подгрупп и общих уроков")
    print("  • Кэширование для каждой подгруппы отдельно")
    print("  • Персональные настройки подгруппы для каждого пользователя")
    print("  • Миграция старых данных к новому формату")
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
        logging.error(f"Ошибка: {e}")


if __name__ == "__main__":
    main()