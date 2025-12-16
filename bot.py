import os
import datetime
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
from database import ScheduleDatabase
from keyboards import create_main_menu
from messages import (
    get_help_message, get_days_list_message, get_subgroups_list_message,
    get_add_instruction_message, format_delete_confirmation_message,
    format_day_command_response, format_full_schedule_by_days,
    format_week_overview, format_all_lessons_message, DAYS_FULL
)

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
DAYS_RU = DAYS_FULL
DAYS_ORDER = {day.lower(): idx for idx, day in enumerate(DAYS_RU)}
VALID_SUBGROUPS = ['1', '2', 'all']

# === КЭШИРОВАНИЕ ДАННЫХ ===
_schedule_cache = {}
_cache_timestamp = None

# === ХРАНЕНИЕ ВЫБРАННОЙ ПОДГРУППЫ ===
user_subgroups = {}


# === УТИЛИТНЫЕ ФУНКЦИИ ===
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
            f"Привет, {user.first_name}! 👋\n"
            f"Текущая подгруппа: 🎯 {subgroup}\n\n{week_overview}",
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
    await update.message.reply_text(get_help_message())


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
            message = f"📅 {today_ru} (подгруппа {subgroup}):\n\n"
            for lesson in lessons:
                message += f"• {lesson['time']} - {lesson['subject']}\n"
        else:
            message = f"🎉 {today_ru}\nСегодня нет уроков для подгруппы {subgroup}!"

        await update.message.reply_text(message)
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
            message = f"📅 {tomorrow_ru} (подгруппа {subgroup}):\n\n"
            for lesson in lessons:
                message += f"• {lesson['time']} - {lesson['subject']}\n"
        else:
            message = f"🎉 {tomorrow_ru}\nЗавтра нет уроков для подгруппы {subgroup}!"

        await update.message.reply_text(message)
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
        message += f"\n\n🎯 Подгруппа: {subgroup}"

        await update.message.reply_text(message)
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

        message = get_days_list_message(subgroup)
        await update.message.reply_text(message)
    except Exception as e:
        print(f"❌ ОШИБКА в schedule_command: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")


async def subgroup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать список подгрупп: /subgroup"""
    try:
        message = get_subgroups_list_message()
        await update.message.reply_text(message)
    except Exception as e:
        print(f"❌ ОШИБКА в subgroup_command: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")


# === КОМАНДЫ ДЛЯ ДНЕЙ ===
async def day_monday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на понедельник: /day_monday"""
    await handle_day_command(update, context, "Понедельник")


async def day_tuesday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на вторник: /day_tuesday"""
    await handle_day_command(update, context, "Вторник")


async def day_wednesday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на среду: /day_wednesday"""
    await handle_day_command(update, context, "Среда")


async def day_thursday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на четверг: /day_thursday"""
    await handle_day_command(update, context, "Четверг")


async def day_friday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на пятницу: /day_friday"""
    await handle_day_command(update, context, "Пятница")


async def day_saturday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на субботу: /day_saturday"""
    await handle_day_command(update, context, "Суббота")


async def day_sunday_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Расписание на воскресенье: /day_sunday"""
    await handle_day_command(update, context, "Воскресенье")


async def handle_day_command(update: Update, context: ContextTypes.DEFAULT_TYPE, day: str):
    """Обработчик команд для дней"""
    try:
        user_id = update.effective_user.id
        subgroup = get_user_subgroup(user_id)

        cached_data = get_cached_schedule(subgroup)
        lessons = cached_data.get(day, [])

        message = format_day_command_response(day, lessons, subgroup)
        await update.message.reply_text(message)

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
            f"✅ Выбрана подгруппа: 🎯 {subgroup}",
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
            await update.message.reply_text(get_add_instruction_message())
            return

        subject, time, day = context.args[0], context.args[1], context.args[2]
        subgroup = context.args[3] if len(context.args) > 3 else 'all'

        if subgroup not in VALID_SUBGROUPS:
            await update.message.reply_text(
                "❌ Некорректная подгруппа. Используйте: 1, 2 или all"
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
            await update.message.reply_text("Укажите ID урока: /delete 1")
            return

        try:
            lesson_id = int(context.args[0])
            lesson = db.get_lesson_by_id(lesson_id)

            if not lesson:
                await update.message.reply_text("❌ Урок не найден")
                return

            message = format_delete_confirmation_message(lesson)
            await update.message.reply_text(message)
        except ValueError:
            await update.message.reply_text("❌ Введите правильный ID (число)")
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
        all_lessons = db.get_all_lessons_sorted()
        message = format_all_lessons_message(all_lessons)
        await update.message.reply_text(message)
    except Exception as e:
        logging.error(f"Ошибка в all_lessons_command: {e}")
        await update.message.reply_text(f"❌ Ошибка при получении уроков: {str(e)}")


async def clear_cache_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Очистка кэша: /clearcache"""
    try:
        clear_schedule_cache()
        await update.message.reply_text("✅ Кэш расписания очищен")
    except Exception as e:
        print(f"❌ ОШИБКА в clear_cache_command: {e}")
        import traceback
        traceback.print_exc()
        await update.message.reply_text(f"❌ Ошибка: {str(e)[:100]}")


# === ОБРАБОТЧИК ТЕКСТОВЫХ СООБЩЕНИЙ (для кнопок клавиатуры) ===
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений от кнопок клавиатуры"""
    try:
        text = update.message.text.lower()
        user_id = update.effective_user.id

        if "сегодня" in text:
            await today_command(update, context)
        elif "завтра" in text:
            await tomorrow_command(update, context)
        elif "вся неделя" in text or "неделя" in text:
            await week_command(update, context)
        elif "добавить урок" in text:
            await update.message.reply_text(get_add_instruction_message())
        elif "удалить урок" in text:
            await update.message.reply_text(
                "🗑️ Для удаления урока используйте команду:\n"
                "/delete <ID_урока>\n\n"
                "Сначала посмотрите ID урока: /all"
            )
        elif "статистика" in text:
            subgroup = get_user_subgroup(user_id)
            stats = db.get_stats_for_subgroup(subgroup)
            message = f"📊 Статистика для подгруппы {subgroup}:\n\n"
            message += f"• Всего уроков: {stats['total_lessons']}\n"
            message += f"• Дней с уроками: {stats['days_with_lessons']}\n"
            message += f"• Разных предметов: {stats['subjects_count']}\n"
            if stats['most_busy_day']:
                message += f"• Самый загруженный день: {stats['most_busy_day']}"
            await update.message.reply_text(message)
        elif "помощь" in text or "❓" in text:
            await help_command(update, context)
        elif "подгруппа" in text:
            await subgroup_command(update, context)
        else:
            await update.message.reply_text(
                "ℹ️ Используйте кнопки ниже или команды:\n"
                "/start - начать\n"
                "/help - помощь\n"
                "/today - сегодня"
            )

    except Exception as e:
        print(f"❌ Ошибка в обработке текста: {e}")
        import traceback
        traceback.print_exc()


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
            ("day_monday", day_monday_command),
            ("day_tuesday", day_tuesday_command),
            ("day_wednesday", day_wednesday_command),
            ("day_thursday", day_thursday_command),
            ("day_friday", day_friday_command),
            ("day_saturday", day_saturday_command),
            ("day_sunday", day_sunday_command),
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
            application.add_handler(CommandHandler(command, handler))

        # Регистрируем динамические команды (confirm_delete_*)
        application.add_handler(MessageHandler(
            filters.Regex(r'^/confirm_delete_\d+$'),
            confirm_delete_command
        ))

        # Регистрируем обработчик текстовых сообщений (для кнопок)
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_text_message
        ))

        print("✅ Бот настроен со следующими командами:")
        for cmd, _ in all_commands:
            print(f"   • /{cmd}")
        print("\n📝 Напишите /start в Telegram")
        print("❓ Напишите /help для списка всех команд")

        application.run_polling(
            poll_interval=2.0,
            timeout=15,
            drop_pending_updates=True,
            close_loop=False
        )

    except KeyboardInterrupt:
        print("\n👋 Бот остановлен")
    except Exception as e:
        print(f"❌ Критическая ошибка при запуске бота: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()