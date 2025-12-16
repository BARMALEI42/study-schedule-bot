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
                    'version': '2.0'
                }
            }
            self._save_data(default_data)

    def _load_data(self) -> Dict:
        try:
            with open(self.db_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.ensure_db_exists()
            return self._load_data()

    def _save_data(self, data: Dict) -> bool:
        data['metadata']['last_modified'] = datetime.now().isoformat()
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True

    # ===== ОСНОВНЫЕ МЕТОДЫ =====
    def add_lesson(self, lesson_data: Dict) -> Dict:
        """Добавить урок с подгруппой"""
        data = self._load_data()
        lesson_id = max([l.get('id', 0) for l in data['schedule']], default=0) + 1

        lesson_data['id'] = lesson_id
        lesson_data['created_at'] = datetime.now().isoformat()
        lesson_data['subgroup'] = lesson_data.get('subgroup', 'all')

        data['schedule'].append(lesson_data)
        self._save_data(data)
        return {'success': True, 'lesson_id': lesson_id}

    def delete_lesson(self, lesson_id: int) -> bool:
        data = self._load_data()
        original_len = len(data['schedule'])
        data['schedule'] = [l for l in data['schedule'] if l.get('id') != lesson_id]

        if len(data['schedule']) < original_len:
            self._save_data(data)
            return True
        return False

    def get_all_lessons(self) -> List[Dict]:
        """Получить все уроки из базы"""
        data = self._load_data()
        return sorted(data.get('schedule', []), key=lambda x: x.get('id', 0))

    def get_lesson_by_id(self, lesson_id: int) -> Optional[Dict]:
        for lesson in self.get_all_lessons():
            if lesson.get('id') == lesson_id:
                return lesson
        return None

    def update_lesson(self, lesson_id: int, updated_data: Dict) -> bool:
        """Обновить данные урока"""
        data = self._load_data()

        for i, lesson in enumerate(data['schedule']):
            if lesson.get('id') == lesson_id:
                # Сохраняем системные поля
                updated_data['id'] = lesson_id
                updated_data['created_at'] = lesson.get('created_at')
                updated_data['updated_at'] = datetime.now().isoformat()
                if 'subgroup' not in updated_data:
                    updated_data['subgroup'] = lesson.get('subgroup', 'all')

                data['schedule'][i] = updated_data
                self._save_data(data)
                return True
        return False

    # ===== МЕТОДЫ ДЛЯ ПОДГРУПП =====
    def _lesson_matches_subgroup(self, lesson: Dict, subgroup: str) -> bool:
        """Проверяет, подходит ли урок для данной подгруппы"""
        lesson_subgroup = lesson.get('subgroup', 'all')

        if subgroup == 'all' or lesson_subgroup == 'all':
            return True

        return str(lesson_subgroup) == str(subgroup)

    def _time_to_minutes(self, time_str: str) -> int:
        """Конвертирует время в минуты для сортировки"""
        try:
            if ':' in time_str:
                hours, minutes = map(int, time_str.split(':'))
                return hours * 60 + minutes
            return 0
        except (ValueError, TypeError):
            return 0

    def get_lessons_by_day_and_subgroup(self, day: str, subgroup: str = 'all') -> List[Dict]:
        """Получить уроки для конкретного дня и подгруппы"""
        day_normalized = day.strip().lower()
        lessons = [
            lesson for lesson in self.get_all_lessons()
            if lesson.get('day', '').strip().lower() == day_normalized
               and self._lesson_matches_subgroup(lesson, subgroup)
        ]
        return sorted(lessons, key=lambda x: self._time_to_minutes(x.get('time', '')))

    def get_all_days_with_lessons_for_subgroup(self, subgroup: str = 'all') -> List[str]:
        """Получить все дни недели с уроками для указанной подгруппы"""
        days_order = {
            'понедельник': 1, 'вторник': 2, 'среда': 3,
            'четверг': 4, 'пятница': 5, 'суббота': 6, 'воскресенье': 7
        }

        days_set = set()
        for lesson in self.get_all_lessons():
            if self._lesson_matches_subgroup(lesson, subgroup):
                day = lesson.get('day', '').strip()
                if day:
                    days_set.add(day.lower())

        sorted_days = sorted(
            list(days_set),
            key=lambda x: days_order.get(x, 99)
        )
        return [day.capitalize() for day in sorted_days]

    def get_stats_for_subgroup(self, subgroup: str = 'all') -> Dict[str, Any]:
        """Статистика по расписанию для указанной подгруппы"""
        lessons = [
            lesson for lesson in self.get_all_lessons()
            if self._lesson_matches_subgroup(lesson, subgroup)
        ]

        if not lessons:
            return {
                'total_lessons': 0,
                'days_with_lessons': 0,
                'subjects_count': 0,
                'subgroup': subgroup
            }

        days_count = {}
        subjects_set = set()

        for lesson in lessons:
            day = lesson.get('day', 'Не указан')
            days_count[day] = days_count.get(day, 0) + 1
            subjects_set.add(lesson.get('subject', ''))

        return {
            'total_lessons': len(lessons),
            'days_with_lessons': len(days_count),
            'subjects_count': len(subjects_set),
            'lessons_by_day': days_count,
            'most_busy_day': max(days_count, key=days_count.get) if days_count else None,
            'subgroup': subgroup
        }

    # ===== ДОПОЛНИТЕЛЬНЫЕ МЕТОДЫ =====
    def search_lessons(self, query: str, subgroup: str = 'all') -> List[Dict]:
        """Поиск уроков по названию предмета"""
        query = query.lower().strip()
        return [
            lesson for lesson in self.get_all_lessons()
            if query in lesson.get('subject', '').lower()
               and self._lesson_matches_subgroup(lesson, subgroup)
        ]

    def get_all_subgroups(self) -> List[str]:
        """Получить все существующие подгруппы"""
        subgroups = {lesson.get('subgroup', 'all') for lesson in self.get_all_lessons()}
        return sorted(list(subgroups))

    def get_lessons_by_subgroup(self, subgroup: str) -> List[Dict]:
        """Получить все уроки для указанной подгруппы"""
        return [
            lesson for lesson in self.get_all_lessons()
            if self._lesson_matches_subgroup(lesson, subgroup)
        ]

    def migrate_to_subgroups(self) -> bool:
        """Миграция старых данных (без подгрупп) к новому формату"""
        data = self._load_data()
        changed = False

        for lesson in data['schedule']:
            if 'subgroup' not in lesson:
                lesson['subgroup'] = 'all'
                changed = True

        if changed:
            self._save_data(data)
        return True

    # ===== МЕТОДЫ ДЛЯ СОРТИРОВКИ (для команды /all) =====
    def get_all_lessons_sorted(self) -> List[Dict]:
        """Получить все уроки, отсортированные по дню и времени"""
        days_order = {
            'понедельник': 1, 'вторник': 2, 'среда': 3,
            'четверг': 4, 'пятница': 5, 'суббота': 6, 'воскресенье': 7
        }

        lessons = self.get_all_lessons()
        return sorted(lessons, key=lambda x: (
            days_order.get(x.get('day', '').lower(), 99),
            self._time_to_minutes(x.get('time', ''))
        ))

    # ===== МЕТОДЫ ДЛЯ СОВМЕСТИМОСТИ =====
    def get_lessons_by_day(self, day: str) -> List[Dict]:
        return self.get_lessons_by_day_and_subgroup(day, 'all')

    def get_all_days_with_lessons(self) -> List[str]:
        return self.get_all_days_with_lessons_for_subgroup('all')

    def get_stats(self) -> Dict[str, Any]:
        return self.get_stats_for_subgroup('all')