import json
import os
from datetime import datetime
from typing import List, Dict, Optional


class ScheduleDatabase:
    def __init__(self, db_file: str = 'schedule.json'):
        self.db_file = db_file
        self.ensure_db_exists()

    def ensure_db_exists(self) -> None:
        """Создаёт файл БД если не существует"""
        if not os.path.exists(self.db_file):
            default_data = {
                'schedule': [],
                'metadata': {'created_at': datetime.now().isoformat()}
            }
            self._save_data(default_data)

    def _load_data(self) -> Dict:
        with open(self.db_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _save_data(self, data: Dict) -> bool:
        with open(self.db_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True

    # CRUD операции
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
        data['schedule'] = [l for l in data['schedule'] if l.get('id') != lesson_id]
        return self._save_data(data)

    def get_all_lessons(self) -> List[Dict]:
        data = self._load_data()
        return data.get('schedule', [])

    def get_lesson_by_id(self, lesson_id: int) -> Optional[Dict]:
        for lesson in self.get_all_lessons():
            if lesson.get('id') == lesson_id:
                return lesson
        return None