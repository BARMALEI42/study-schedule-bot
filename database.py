import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Any


class ScheduleDatabase:
    def __init__(self, db_file: str = 'schedule.json'):
        self.db_file = db_file
        self.ensure_db_exists()

    def ensure_db_exists(self) -> None:
        """Создаёт файл БД если не существует"""
        if not os.path.exists(self.db_file):
            default_data = {
                'schedule': [],
                'metadata': {
                    'created_at': datetime.now().isoformat(),
                    'last_modified': datetime.now().isoformat(),
                    'version': '2.0'  # Версия с поддержкой подгрупп
                }
            }
            self._save_data(default_data)

    def _load_data(self) -> Dict:
        with open(self.db_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_data(self, data: Dict) -> bool:
        data['metadata']['last_modified'] = datetime.now().isoformat()
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True

    # ===== БАЗОВЫЕ МЕТОДЫ =====
    def add_lesson(self, lesson_data: Dict) -> Dict:
        """Добавить урок с подгруппой"""
        data = self._load_data()
        lesson_id = len(data['schedule']) + 1

        # Устанавливаем подгруппу по умолчанию, если не указана
        if 'subgroup' not in lesson_data:
            lesson_data['subgroup'] = 'all'  # для всех подгрупп

        lesson_data['id'] = lesson_id
        lesson_data['created_at'] = datetime.now().isoformat()
        data['schedule'].append(lesson_data)
        self._save_data(data)
        return {'success': True, 'lesson_id': lesson_id}

    def delete_lesson(self, lesson_id: int) -> bool:
        data = self._load_data()
        original_count = len(data['schedule'])
        data['schedule'] = [l for l in data['schedule'] if l.get('id') != lesson_id]
        deleted = len(data['schedule']) < original_count
        if deleted:
            self._save_data(data)
        return deleted

    def get_all_lessons(self) -> List[Dict]:
        data = self._load_data()
        return data.get('schedule', [])

    def get_lesson_by_id(self, lesson_id: int) -> Optional[Dict]:
        for lesson in self.get_all_lessons():
            if lesson.get('id') == lesson_id:
                return lesson
        return None

    # ===== МЕТОДЫ ДЛЯ РАБОТЫ С ПОДГРУППАМИ =====
    def get_lessons_by_day_and_subgroup(self, day: str, subgroup: str = 'all') -> List[Dict]:
        """Получить уроки для конкретного дня и подгруппы"""
        day_lower = day.lower().strip()
        all_lessons = self.get_all_lessons()

        # Фильтруем по дню и подгруппе
        filtered_lessons = [
            lesson for lesson in all_lessons
            if lesson.get('day', '').lower().strip() == day_lower
               and self._lesson_matches_subgroup(lesson, subgroup)
        ]

        # Сортируем по времени
        return sorted(filtered_lessons, key=lambda x: self._time_to_minutes(x.get('time', '')))

    def _lesson_matches_subgroup(self, lesson: Dict, subgroup: str) -> bool:
        """Проверяет, подходит ли урок для данной подгруппы"""
        lesson_subgroup = lesson.get('subgroup', 'all')

        if lesson_subgroup == 'all':
            return True  # Урок для всех подгрупп

        if subgroup == 'all':
            return True  # Пользователь хочет видеть все уроки

        # Урок для конкретной подгруппы
        return str(lesson_subgroup) == str(subgroup)

    def _time_to_minutes(self, time_str: str) -> int:
        """Конвертирует время в минуты для сортировки"""
        try:
            if ':' in time_str:
                hours, minutes = map(int, time_str.split(':'))
                return hours * 60 + minutes
            return 0
        except:
            return 0

    def get_all_days_with_lessons_for_subgroup(self, subgroup: str = 'all') -> List[str]:
        """Получить все дни недели с уроками для указанной подгруппы"""
        all_lessons = self.get_all_lessons()

        # Фильтруем уроки по подгруппе
        filtered_lessons = [
            lesson for lesson in all_lessons
            if self._lesson_matches_subgroup(lesson, subgroup)
        ]

        # Получаем уникальные дни
        days_set = {lesson.get('day', '') for lesson in filtered_lessons if lesson.get('day')}

        # Сортируем дни по порядку недели
        days_order = {
            'понедельник': 1, 'вторник': 2, 'среда': 3,
            'четверг': 4, 'пятница': 5, 'суббота': 6, 'воскресенье': 7
        }

        days_lower = [day.lower() for day in days_set]
        sorted_days = sorted(
            days_lower,
            key=lambda x: days_order.get(x, 99)
        )

        return [day.capitalize() for day in sorted_days]

    def get_lessons_by_week_for_subgroup(self, subgroup: str = 'all') -> Dict[str, List[Dict]]:
        """Получить все уроки на неделю для указанной подгруппы"""
        result = {}

        # Инициализируем все дни недели
        week_days = ['Понедельник', 'Вторник', 'Среда', 'Четверг',
                     'Пятница', 'Суббота', 'Воскресеньe']

        for day in week_days:
            result[day] = self.get_lessons_by_day_and_subgroup(day, subgroup)

        return result

    def update_lesson(self, lesson_id: int, updated_data: Dict) -> bool:
        """Обновить данные урока"""
        data = self._load_data()

        for i, lesson in enumerate(data['schedule']):
            if lesson.get('id') == lesson_id:
                # Сохраняем неизменяемые поля
                updated_data['id'] = lesson_id
                updated_data['created_at'] = lesson.get('created_at')
                updated_data['updated_at'] = datetime.now().isoformat()

                data['schedule'][i] = updated_data
                self._save_data(data)
                return True

        return False

    def search_lessons(self, query: str, subgroup: str = 'all') -> List[Dict]:
        """Поиск уроков по названию предмета для указанной подгруппы"""
        query = query.lower().strip()
        all_lessons = self.get_all_lessons()

        return [
            lesson for lesson in all_lessons
            if query in lesson.get('subject', '').lower()
               and self._lesson_matches_subgroup(lesson, subgroup)
        ]

    def clear_day_for_subgroup(self, day: str, subgroup: str = 'all') -> bool:
        """Удалить все уроки в указанный день для указанной подгруппы"""
        data = self._load_data()
        original_count = len(data['schedule'])

        # Фильтруем уроки, которые НЕ нужно удалять
        data['schedule'] = [
            lesson for lesson in data['schedule']
            if not (lesson.get('day', '').lower() == day.lower()
                    and self._lesson_matches_subgroup(lesson, subgroup))
        ]

        deleted = len(data['schedule']) < original_count
        if deleted:
            self._save_data(data)
        return deleted

    def get_stats_for_subgroup(self, subgroup: str = 'all') -> Dict[str, Any]:
        """Статистика по расписанию для указанной подгруппы"""
        all_lessons = self.get_all_lessons()

        # Фильтруем уроки по подгруппе
        filtered_lessons = [
            lesson for lesson in all_lessons
            if self._lesson_matches_subgroup(lesson, subgroup)
        ]

        if not filtered_lessons:
            return {
                'total_lessons': 0,
                'days_with_lessons': 0,
                'subjects_count': 0,
                'subgroup': subgroup
            }

        # Количество уроков по дням
        days_count = {}
        subjects_set = set()

        for lesson in filtered_lessons:
            day = lesson.get('day', 'Не указан')
            days_count[day] = days_count.get(day, 0) + 1
            subjects_set.add(lesson.get('subject', ''))

        return {
            'total_lessons': len(filtered_lessons),
            'days_with_lessons': len(days_count),
            'subjects_count': len(subjects_set),
            'lessons_by_day': days_count,
            'most_busy_day': max(days_count.items(), key=lambda x: x[1])[0] if days_count else None,
            'subgroup': subgroup
        }

    # ===== СТАРЫЕ МЕТОДЫ ДЛЯ СОВМЕСТИМОСТИ (чтобы не сломать существующий код) =====
    def get_lessons_by_day(self, day: str) -> List[Dict]:
        """Старый метод для совместимости (возвращает для всех подгрупп)"""
        return self.get_lessons_by_day_and_subgroup(day, 'all')

    def get_all_days_with_lessons(self) -> List[str]:
        """Старый метод для совместимости (возвращает для всех подгрупп)"""
        return self.get_all_days_with_lessons_for_subgroup('all')

    def get_lessons_by_week(self) -> Dict[str, List[Dict]]:
        """Старый метод для совместимости (возвращает для всех подгрупп)"""
        return self.get_lessons_by_week_for_subgroup('all')

    def get_stats(self) -> Dict[str, Any]:
        """Старый метод для совместимости (возвращает для всех подгрупп)"""
        return self.get_stats_for_subgroup('all')

    def clear_day(self, day: str) -> bool:
        """Старый метод для совместимости (очищает для всех подгрупп)"""
        return self.clear_day_for_subgroup(day, 'all')

    # ===== ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ ДЛЯ ПОДГРУПП =====
    def get_all_subgroups(self) -> List[str]:
        """Получить все существующие подгруппы"""
        all_lessons = self.get_all_lessons()
        subgroups_set = {lesson.get('subgroup', 'all') for lesson in all_lessons}
        return sorted(list(subgroups_set))

    def get_lessons_by_subgroup(self, subgroup: str) -> List[Dict]:
        """Получить все уроки для указанной подгруппы"""
        all_lessons = self.get_all_lessons()
        return [
            lesson for lesson in all_lessons
            if self._lesson_matches_subgroup(lesson, subgroup)
        ]

    def migrate_to_subgroups(self):
        """Миграция старых данных (без подгрупп) к новому формату"""
        data = self._load_data()

        for lesson in data['schedule']:
            if 'subgroup' not in lesson:
                lesson['subgroup'] = 'all'

        self._save_data(data)
        return True