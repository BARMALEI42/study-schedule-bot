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
                    'last_modified': datetime.now().isoformat()
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

    # ===== СУЩЕСТВУЮЩИЕ МЕТОДЫ (оставить без изменений) =====
    def add_lesson(self, lesson_data: Dict) -> Dict:
        data = self._load_data()
        lesson_id = len(data['schedule']) + 1
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

    # ===== НОВЫЕ МЕТОДЫ ДЛЯ РАБОТЫ С ДНЯМИ НЕДЕЛИ =====

    def get_lessons_by_day(self, day: str) -> List[Dict]:
        """Получить все уроки для конкретного дня недели"""
        day_lower = day.lower().strip()
        all_lessons = self.get_all_lessons()

        # Сортируем по времени
        day_lessons = [
            lesson for lesson in all_lessons
            if lesson.get('day', '').lower().strip() == day_lower
        ]

        # Сортируем по времени
        return sorted(day_lessons, key=lambda x: self._time_to_minutes(x.get('time', '')))

    def _time_to_minutes(self, time_str: str) -> int:
        """Конвертирует время в минуты для сортировки"""
        try:
            if ':' in time_str:
                hours, minutes = map(int, time_str.split(':'))
                return hours * 60 + minutes
            return 0
        except:
            return 0

    def get_all_days_with_lessons(self) -> List[str]:
        """Получить все дни недели, в которых есть уроки (уникальные)"""
        all_lessons = self.get_all_lessons()
        days_set = {lesson.get('day', '') for lesson in all_lessons if lesson.get('day')}

        # Сортируем дни по порядку недели
        days_order = {
            'понедельник': 1, 'вторник': 2, 'среда': 3,
            'четверг': 4, 'пятница': 5, 'суббота': 6, 'воскресенье': 7
        }

        # Приводим к нижнему регистру для сравнения
        days_lower = [day.lower() for day in days_set]

        # Сортируем по порядку дней недели
        sorted_days = sorted(
            days_lower,
            key=lambda x: days_order.get(x, 99)
        )

        # Возвращаем с заглавной буквы
        return [day.capitalize() for day in sorted_days]

    def get_lessons_by_week(self) -> Dict[str, List[Dict]]:
        """Получить все уроки, сгруппированные по дням недели"""
        result = {}

        # Инициализируем все дни недели
        week_days = ['Понедельник', 'Вторник', 'Среда', 'Четверг',
                     'Пятница', 'Суббота', 'Воскресенье']

        for day in week_days:
            result[day] = self.get_lessons_by_day(day)

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

    def search_lessons(self, query: str) -> List[Dict]:
        """Поиск уроков по названию предмета"""
        query = query.lower().strip()
        all_lessons = self.get_all_lessons()

        return [
            lesson for lesson in all_lessons
            if query in lesson.get('subject', '').lower()
        ]

    def clear_day(self, day: str) -> bool:
        """Удалить все уроки в указанный день"""
        data = self._load_data()
        original_count = len(data['schedule'])

        data['schedule'] = [
            lesson for lesson in data['schedule']
            if lesson.get('day', '').lower() != day.lower()
        ]

        deleted = len(data['schedule']) < original_count
        if deleted:
            self._save_data(data)
        return deleted

    def get_stats(self) -> Dict[str, Any]:
        """Статистика по расписанию"""
        all_lessons = self.get_all_lessons()

        if not all_lessons:
            return {
                'total_lessons': 0,
                'days_with_lessons': 0,
                'subjects_count': 0
            }

        # Количество уроков по дням
        days_count = {}
        subjects_set = set()

        for lesson in all_lessons:
            day = lesson.get('day', 'Не указан')
            days_count[day] = days_count.get(day, 0) + 1
            subjects_set.add(lesson.get('subject', ''))

        return {
            'total_lessons': len(all_lessons),
            'days_with_lessons': len(days_count),
            'subjects_count': len(subjects_set),
            'lessons_by_day': days_count,
            'most_busy_day': max(days_count.items(), key=lambda x: x[1])[0] if days_count else None
        }