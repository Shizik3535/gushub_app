import sqlite3
from typing import List, Optional, Dict

class LocalCourseDB:
    def __init__(self, db_path: str = 'local_courses.db') -> None:
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                github_path TEXT UNIQUE,
                site_id INTEGER,
                title TEXT,
                description TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER,
                github_path TEXT,
                site_id INTEGER,
                title TEXT,
                description TEXT,
                FOREIGN KEY(course_id) REFERENCES courses(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id INTEGER,
                github_path TEXT,
                site_id INTEGER,
                title TEXT,
                raw_url TEXT,
                FOREIGN KEY(module_id) REFERENCES modules(id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lesson_id INTEGER,
                github_path TEXT,
                site_id INTEGER,
                title TEXT,
                raw_url TEXT,
                FOREIGN KEY(lesson_id) REFERENCES lessons(id)
            )
        ''')
        self.conn.commit()

    # --- Добавление ---
    def add_course(self, github_path: str, title: str, description: str | None = None, site_id: int | None = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO courses (github_path, site_id, title, description) 
            VALUES (?, ?, ?, ?)
        ''', (github_path, site_id, title, description))
        self.conn.commit()
        return cursor.lastrowid

    def add_module(self, course_id: int, github_path: str, title: str, description: str | None = None, site_id: int | None = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO modules (course_id, github_path, site_id, title, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (course_id, github_path, site_id, title, description))
        self.conn.commit()
        return cursor.lastrowid

    def add_lesson(self, module_id: int, github_path: str, title: str, raw_url: str, site_id: int | None = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO lessons (module_id, github_path, site_id, title, raw_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (module_id, github_path, site_id, title, raw_url))
        self.conn.commit()
        return cursor.lastrowid

    def add_task(self, lesson_id: int, github_path: str, title: str, raw_url: str, site_id: int | None = None) -> int:
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (lesson_id, github_path, site_id, title, raw_url)
            VALUES (?, ?, ?, ?, ?)
        ''', (lesson_id, github_path, site_id, title, raw_url))
        self.conn.commit()
        return cursor.lastrowid

    # --- Получение ---
    def get_all_courses(self) -> list[dict[str, object]]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM courses')
        rows = cursor.fetchall()
        return [{description[0]: row[i] for i, description in enumerate(cursor.description)} for row in rows]

    def get_course(self, course_id: int) -> dict[str, object] | None:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM courses WHERE id = ?', (course_id,))
        row = cursor.fetchone()
        if row:
            return {description[0]: row[i] for i, description in enumerate(cursor.description)}
        return None

    def get_courses(self) -> List[Dict]:
        """Получение списка всех курсов"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM courses ORDER BY title
        """)
        rows = cursor.fetchall()
        return [{description[0]: row[i] for i, description in enumerate(cursor.description)} for row in rows]

    def get_modules(self, course_id: int) -> list[dict[str, object]]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM modules WHERE course_id = ?', (course_id,))
        rows = cursor.fetchall()
        return [{description[0]: row[i] for i, description in enumerate(cursor.description)} for row in rows]

    def get_lessons(self, module_id: int) -> list[dict[str, object]]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM lessons WHERE module_id = ?', (module_id,))
        rows = cursor.fetchall()
        return [{description[0]: row[i] for i, description in enumerate(cursor.description)} for row in rows]

    def get_tasks(self, lesson_id: int) -> list[dict[str, object]]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE lesson_id = ?', (lesson_id,))
        rows = cursor.fetchall()
        return [{description[0]: row[i] for i, description in enumerate(cursor.description)} for row in rows]

    def get_course_by_module(self, module_id: int) -> dict[str, object] | None:
        """Получение курса по ID модуля"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT c.* FROM courses c
            JOIN modules m ON m.course_id = c.id
            WHERE m.id = ?
        ''', (module_id,))
        row = cursor.fetchone()
        if row:
            return {description[0]: row[i] for i, description in enumerate(cursor.description)}
        return None

    def get_module(self, module_id: int) -> dict[str, object] | None:
        """Получение модуля по ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM modules WHERE id = ?', (module_id,))
        row = cursor.fetchone()
        if row:
            return {description[0]: row[i] for i, description in enumerate(cursor.description)}
        return None

    def get_module_by_lesson(self, lesson_id: int) -> dict | None:
        """Получение модуля по ID урока"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT m.* FROM modules m
            JOIN lessons l ON m.id = l.module_id
            WHERE l.id = ?
        """, (lesson_id,))
        row = cursor.fetchone()
        if row:
            return {
                'id': row[0],
                'course_id': row[1],
                'github_path': row[2],
                'title': row[3],
                'description': row[4]
            }
        return None

    def get_lesson(self, lesson_id: int) -> dict[str, object] | None:
        """Получение урока по ID"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM lessons WHERE id = ?', (lesson_id,))
        row = cursor.fetchone()
        if row:
            return {description[0]: row[i] for i, description in enumerate(cursor.description)}
        return None

    def get_task(self, task_id: int) -> dict[str, object] | None:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT * FROM tasks WHERE id = ?",
            (task_id,)
        )
        row = cursor.fetchone()
        if row:
            columns = [column[0] for column in cursor.description]
            return dict(zip(columns, row))
        return None

    # --- Обновление ---
    def update_course(self, course_id: int, **fields: object) -> None:
        self._update_table('courses', course_id, fields)

    def update_module(self, module_id: int, **fields: object) -> None:
        self._update_table('modules', module_id, fields)

    def update_lesson(self, lesson_id: int, **fields: object) -> None:
        self._update_table('lessons', lesson_id, fields)

    def update_task(self, task_id: int, **fields: object) -> None:
        self._update_table('tasks', task_id, fields)

    def _update_table(self, table: str, row_id: int, fields: dict[str, object]) -> None:
        if not fields:
            return
        cursor = self.conn.cursor()
        columns = ', '.join(f"{k} = ?" for k in fields.keys())
        values = list(fields.values())
        values.append(row_id)
        sql = f"UPDATE {table} SET {columns} WHERE id = ?"
        cursor.execute(sql, values)
        self.conn.commit()

    # --- Каскадное удаление ---
    def delete_course(self, course_id: int) -> None:
        modules = self.get_modules(course_id)
        for module in modules:
            self.delete_module(module['id'])
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM courses WHERE id = ?', (course_id,))
        self.conn.commit()

    def delete_module(self, module_id: int) -> None:
        lessons = self.get_lessons(module_id)
        for lesson in lessons:
            self.delete_lesson(lesson['id'])
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM modules WHERE id = ?', (module_id,))
        self.conn.commit()

    def delete_lesson(self, lesson_id: int) -> None:
        tasks = self.get_tasks(lesson_id)
        for task in tasks:
            self.delete_task(task['id'])
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM lessons WHERE id = ?', (lesson_id,))
        self.conn.commit()

    def delete_task(self, task_id: int) -> None:
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        self.conn.commit()

    def close(self) -> None:
        self.conn.close()
