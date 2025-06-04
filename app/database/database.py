import sqlite3


class Database:
    def __init__(self, db_path: str = "database.db") -> None:
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                github_path TEXT UNIQUE,
                title TEXT UNIQUE,
                description TEXT,
                site_id INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER,
                github_path TEXT UNIQUE,
                title TEXT,
                description TEXT,
                site_id INTEGER,
                FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                module_id INTEGER,
                github_path TEXT UNIQUE,
                title TEXT,
                raw_url TEXT,
                site_id INTEGER,
                FOREIGN KEY(module_id) REFERENCES modules(id) ON DELETE CASCADE
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lesson_id INTEGER,
                github_path TEXT UNIQUE,
                title TEXT,
                raw_url TEXT,
                site_id INTEGER,
                FOREIGN KEY(lesson_id) REFERENCES lessons(id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()

    # --- Курсы ---
    def add_course(self, github_path: str, title: str, description: str | None = None, site_id: int | None = None) -> int:
        """Добавление курса в базу данных"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO courses (github_path, title, description, site_id)
            VALUES (?, ?, ?, ?)
        ''', (github_path, title, description, site_id))
        self.conn.commit()
        return cursor.lastrowid

    def get_course(self, course_id: int) -> dict[str, object] | None:
        """Получение курса по его id"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM courses WHERE id = ?
        ''', (course_id,))
        row = cursor.fetchone()
        if row:
            return {description[0]: row[i] for i, description in enumerate(cursor.description)}
        return None

    def get_courses(self) -> list[dict[str, object]]:
        """Получение всех курсов"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM courses ORDER BY title
        ''')
        rows = cursor.fetchall()
        if rows:
            return [{description[0]: row[i] for i, description in enumerate(cursor.description)} for row in rows]
        return []
    
    def delete_course(self, course_id: int) -> None:
        """Удаление курса из базы данных"""
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM courses WHERE id = ?
        ''', (course_id,))
        self.conn.commit()
    
    # --- Модули ---
    def add_module(self, course_id: int, github_path: str, title: str, description: str | None = None, site_id: int | None = None) -> int:
        """Добавление модуля в базу данных"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO modules (course_id, github_path, title, description, site_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (course_id, github_path, title, description, site_id))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_module(self, module_id: int) -> dict[str, object] | None:
        """Получение модуля по его id"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM modules WHERE id = ?
        ''', (module_id,))
        row = cursor.fetchone()
        if row:
            return {description[0]: row[i] for i, description in enumerate(cursor.description)}
        return None
    
    def get_modules(self) -> list[dict[str, object]]:
        """Получение всех модулей"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM modules ORDER BY title
        ''')
        rows = cursor.fetchall()
        if rows:
            return [{description[0]: row[i] for i, description in enumerate(cursor.description)} for row in rows]
        return []
    
    def get_modules_by_course(self, course_id: int) -> list[dict[str, object]]:
        """Получение всех модулей по курсу"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM modules WHERE course_id = ?
        ''', (course_id,))
        rows = cursor.fetchall()
        if rows:
            return [{description[0]: row[i] for i, description in enumerate(cursor.description)} for row in rows]
        return []
    
    def delete_module(self, module_id: int) -> None:
        """Удаление модуля из базы данных"""
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM modules WHERE id = ?
        ''', (module_id,))
        self.conn.commit()
    
    # --- Уроки ---
    def add_lesson(self, module_id: int, github_path: str, title: str, raw_url: str, site_id: int | None = None) -> int:
        """Добавление урока в базу данных"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO lessons (module_id, github_path, title, raw_url, site_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (module_id, github_path, title, raw_url, site_id))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_lesson(self, lesson_id: int) -> dict[str, object] | None:
        """Получение урока по его id"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM lessons WHERE id = ?
        ''', (lesson_id,))
        row = cursor.fetchone()
        if row:
            return {description[0]: row[i] for i, description in enumerate(cursor.description)}
        return None
    
    def get_lessons(self) -> list[dict[str, object]]:
        """Получение всех уроков"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM lessons ORDER BY title
        ''')
        rows = cursor.fetchall()
        if rows:
            return [{description[0]: row[i] for i, description in enumerate(cursor.description)} for row in rows]
        return []
    
    def get_lessons_by_module(self, module_id: int) -> dict[str, object] | None:
        """Получение урока по модулю"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM lessons WHERE module_id = ?
        ''', (module_id,))
        rows = cursor.fetchall()
        if rows:
            return [{description[0]: row[i] for i, description in enumerate(cursor.description)} for row in rows]
        return []
    
    def delete_lesson(self, lesson_id: int) -> None:
        """Удаление урока из базы данных"""
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM lessons WHERE id = ?
        ''', (lesson_id,))
        self.conn.commit()

    # --- Задачи ---
    def add_task(self, lesson_id: int, github_path: str, title: str, raw_url: str, site_id: int | None = None) -> int:
        """Добавление задачи в базу данных"""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO tasks (lesson_id, github_path, title, raw_url, site_id)
            VALUES (?, ?, ?, ?, ?)
        ''', (lesson_id, github_path, title, raw_url, site_id))
        self.conn.commit()
        return cursor.lastrowid
    
    def get_task(self, task_id: int) -> dict[str, object] | None:   
        """Получение задачи по его id"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM tasks WHERE id = ?
        ''', (task_id,))
        row = cursor.fetchone()
        if row:
            return {description[0]: row[i] for i, description in enumerate(cursor.description)}
        return None
    
    def get_tasks(self) -> list[dict[str, object]]:
        """Получение всех задач"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM tasks ORDER BY title
        ''')
        rows = cursor.fetchall()
        if rows:
            return [{description[0]: row[i] for i, description in enumerate(cursor.description)} for row in rows]
        return []
    
    def get_tasks_by_lesson(self, lesson_id: int) -> list[dict[str, object]]:
        """Получение всех задач по уроку"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM tasks WHERE lesson_id = ?
        ''', (lesson_id,))
        rows = cursor.fetchall()
        if rows:
            return [{description[0]: row[i] for i, description in enumerate(cursor.description)} for row in rows]
        return []

    def delete_task(self, task_id: int) -> None:
        """Удаление задачи из базы данных"""
        cursor = self.conn.cursor()
        cursor.execute('''
            DELETE FROM tasks WHERE id = ?
        ''', (task_id,))
        self.conn.commit()

    def close(self) -> None:
        """Закрытие соединения с базой данных"""
        self.conn.close()

