from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QMessageBox,
    QFileDialog
)
from PyQt6.QtCore import pyqtSignal
from app_test.database.local_db import LocalCourseDB
from app_test.api.github_api import GitHubCourseManager


class LessonsPage(QWidget):
    lesson_selected = pyqtSignal(int)  # Сигнал для выбора урока
    task_creation_requested = pyqtSignal(int)  # Сигнал для создания задачи
    lesson_deleted = pyqtSignal()  # Сигнал для обновления боковой панели после удаления урока

    def __init__(self, db: LocalCourseDB, github_api: GitHubCourseManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.github_api = github_api
        self.current_lesson_id = None
        self.current_module_id = None
        self.current_course_id = None
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        # Заголовок
        self.title_label = QLabel("Уроки")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        # Форма урока
        form_layout = QVBoxLayout()
        
        # Название
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Название:"))
        self.title_input = QLineEdit()
        title_layout.addWidget(self.title_input)
        form_layout.addLayout(title_layout)

        # Выбор файла
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Файл урока:"))
        self.file_path_input = QLineEdit()
        self.file_path_input.setReadOnly(True)
        file_layout.addWidget(self.file_path_input)
        self.browse_button = QPushButton("Обзор...")
        self.browse_button.clicked.connect(self.browse_file)
        file_layout.addWidget(self.browse_button)
        form_layout.addLayout(file_layout)

        self.layout.addLayout(form_layout)
        self.layout.addStretch()

        # Кнопки управления (внизу)
        buttons_layout = QHBoxLayout()
        self.create_button = QPushButton("Создать урок")
        self.create_button.clicked.connect(self.create_lesson)
        self.update_button = QPushButton("Обновить урок")
        self.update_button.clicked.connect(self.update_lesson)
        self.update_button.setEnabled(False)  # По умолчанию отключена
        self.delete_button = QPushButton("Удалить урок")
        self.delete_button.clicked.connect(self.delete_lesson)
        self.create_task_button = QPushButton("Создать задачу")
        self.create_task_button.clicked.connect(self.create_task)
        self.create_task_button.setEnabled(False)  # По умолчанию отключена

        buttons_layout.addWidget(self.create_button)
        buttons_layout.addWidget(self.update_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.create_task_button)
        self.layout.addLayout(buttons_layout)

    def browse_file(self):
        """Открытие диалога выбора файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл урока",
            "",
            "Markdown Files (*.md)"
        )
        if file_path:
            self.file_path_input.setText(file_path)

    def load_lesson(self, lesson_id: int | None, module_id: int, course_id: int):
        """Загрузка данных урока"""
        self.current_lesson_id = lesson_id
        self.current_module_id = module_id
        self.current_course_id = course_id
        if lesson_id:
            lesson = self.db.get_lesson(lesson_id)
            if lesson:
                self.title_input.setText(lesson['title'])
                self.file_path_input.setText(lesson['github_path'] or '')
                self.create_task_button.setEnabled(True)
                self.update_button.setEnabled(True)
                self.delete_button.setEnabled(True)
            else:
                self.clear_form()
        else:
            # Если lesson_id None, значит создаем новый урок
            self.clear_form()
            self.create_task_button.setEnabled(False)
            self.update_button.setEnabled(False)
            self.delete_button.setEnabled(False)

    def clear_form(self):
        """Очистка формы"""
        self.current_lesson_id = None
        # Не очищаем current_module_id и current_course_id, так как они должны сохраняться
        self.title_input.clear()
        self.file_path_input.clear()
        self.create_task_button.setEnabled(False)
        self.update_button.setEnabled(False)
        self.delete_button.setEnabled(False)

    def update_lesson(self):
        """Обновление урока"""
        if not self.current_lesson_id:
            QMessageBox.warning(self, "Ошибка", "Не выбран урок для обновления")
            return

        title = self.title_input.text().strip()
        file_path = self.file_path_input.text().strip()

        if not title:
            QMessageBox.warning(self, "Ошибка", "Название урока не может быть пустым")
            return

        # Проверяем, что название не изменилось
        lesson = self.db.get_lesson(self.current_lesson_id)
        if lesson and lesson['title'] != title:
            QMessageBox.warning(self, "Ошибка", "Название урока нельзя изменить")
            return

        # Проверяем, что выбран новый файл
        if not file_path or file_path == lesson['github_path']:
            QMessageBox.warning(self, "Ошибка", "Выберите новый файл для обновления урока")
            return

        try:
            # Читаем содержимое файла
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            course = self.db.get_course(self.current_course_id)
            if not course:
                raise ValueError("Курс не найден")

            # Обновляем урок в GitHub
            repo = self.github_api.github.get_repo(f"{self.github_api.user.login}/{course['github_path']}")
            try:
                # Получаем содержимое файла для получения SHA
                contents = repo.get_contents(lesson['github_path'])
                if isinstance(contents, list):
                    # Если это список (директория), берем первый элемент
                    contents = contents[0]
                # Обновляем файл
                repo.update_file(
                    lesson['github_path'],
                    f"Update lesson: {title}",
                    content,
                    contents.sha
                )
            except Exception as e:
                raise Exception(f"Не удалось обновить файл в GitHub: {str(e)}")

            # Обновляем урок в локальной БД
            self.db.update_lesson(
                self.current_lesson_id,
                title=title,
                github_path=lesson['github_path']
            )

            QMessageBox.information(self, "Успех", "Урок успешно обновлен")
            self.lesson_selected.emit(self.current_lesson_id)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить урок: {str(e)}")

    def create_lesson(self):
        """Создание нового урока"""
        if not self.current_module_id:
            QMessageBox.warning(self, "Ошибка", "Не выбран модуль для создания урока")
            return

        title = self.title_input.text().strip()
        file_path = self.file_path_input.text().strip()

        if not title:
            QMessageBox.warning(self, "Ошибка", "Название урока не может быть пустым")
            return

        if not file_path:
            QMessageBox.warning(self, "Ошибка", "Не выбран файл урока")
            return

        # Проверяем уникальность названия урока внутри модуля
        lessons = self.db.get_lessons(self.current_module_id)
        for lesson in lessons:
            if lesson['title'].lower() == title.lower():
                QMessageBox.warning(self, "Ошибка", "Урок с таким названием уже существует в этом модуле")
                return

        try:
            # Читаем содержимое файла
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            module = self.db.get_module(self.current_module_id)
            course = self.db.get_course(self.current_course_id)
            if not module or not course:
                raise ValueError("Модуль или курс не найден")

            # Создаем урок в GitHub
            repo = self.github_api.github.get_repo(f"{self.github_api.user.login}/{course['github_path']}")
            lesson_path = self.github_api.create_lesson(
                repo, 
                module['github_path'], 
                title, 
                content,
                f"Add lesson: {title}"
            )
            
            # Создаем урок в локальной БД
            lesson_id = self.db.add_lesson(
                module_id=self.current_module_id,
                github_path=lesson_path,
                title=title,
                raw_url=lesson_path
            )

            QMessageBox.information(self, "Успех", "Урок успешно создан")
            self.lesson_selected.emit(lesson_id)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать урок: {str(e)}")

    def delete_lesson(self):
        """Удаление текущего урока"""
        if not self.current_lesson_id:
            QMessageBox.warning(self, "Ошибка", "Не выбран урок для удаления")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить этот урок?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                lesson = self.db.get_lesson(self.current_lesson_id)
                course = self.db.get_course(self.current_course_id)
                if lesson and course and lesson.get('github_path'):
                    # Удаляем урок из GitHub
                    repo = self.github_api.github.get_repo(f"{self.github_api.user.login}/{course['github_path']}")
                    try:
                        # Получаем содержимое файла для получения SHA
                        contents = repo.get_contents(lesson['github_path'])
                        if isinstance(contents, list):
                            # Если это список (директория), берем первый элемент
                            contents = contents[0]
                        # Удаляем файл
                        repo.delete_file(
                            lesson['github_path'],
                            f"Delete lesson: {lesson['title']}",
                            contents.sha
                        )
                    except Exception as e:
                        # Если файл не найден, возможно он уже удален
                        print(f"Warning: Could not get file contents: {str(e)}")

                    # Удаляем все задачи урока из GitHub
                    tasks = self.db.get_tasks(self.current_lesson_id)
                    for task in tasks:
                        if task.get('github_path'):
                            try:
                                contents = repo.get_contents(task['github_path'])
                                if isinstance(contents, list):
                                    contents = contents[0]
                                repo.delete_file(
                                    task['github_path'],
                                    f"Delete task: {task['title']}",
                                    contents.sha
                                )
                            except Exception as e:
                                print(f"Warning: Could not delete task file: {str(e)}")
                
                # Удаляем урок и все его задачи из локальной БД
                self.db.delete_lesson(self.current_lesson_id)
                
                QMessageBox.information(self, "Успех", "Урок успешно удален")
                self.clear_form()
                # Отправляем сигнал об удалении урока
                self.lesson_deleted.emit()
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить урок: {str(e)}")

    def create_task(self):
        """Запрос на создание задачи"""
        if self.current_lesson_id:
            self.task_creation_requested.emit(self.current_lesson_id)
