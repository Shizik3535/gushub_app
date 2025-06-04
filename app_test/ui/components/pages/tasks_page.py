from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTextEdit, QMessageBox,
    QFileDialog
)
from PyQt6.QtCore import pyqtSignal
from app_test.database.local_db import LocalCourseDB
from app_test.api.github_api import GitHubCourseManager


class TasksPage(QWidget):
    task_selected = pyqtSignal(int)  # Сигнал для выбора задачи
    task_deleted = pyqtSignal()  # Сигнал для обновления боковой панели после удаления задачи

    def __init__(self, db: LocalCourseDB, github_api: GitHubCourseManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.github_api = github_api
        self.current_task_id = None
        self.current_lesson_id = None
        self.current_module_id = None
        self.current_course_id = None
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        # Заголовок
        self.title_label = QLabel("Задачи")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        # Форма задачи
        form_layout = QVBoxLayout()
        
        # Название
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Название:"))
        self.title_input = QLineEdit()
        title_layout.addWidget(self.title_input)
        form_layout.addLayout(title_layout)

        # Файл решения
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Файл задания:"))
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
        self.create_button = QPushButton("Создать задачу")
        self.create_button.clicked.connect(self.create_task)
        self.update_button = QPushButton("Обновить задачу")
        self.update_button.clicked.connect(self.update_task)
        self.update_button.setEnabled(False)
        self.delete_button = QPushButton("Удалить задачу")
        self.delete_button.clicked.connect(self.delete_task)
        self.delete_button.setEnabled(False)

        buttons_layout.addWidget(self.create_button)
        buttons_layout.addWidget(self.update_button)
        buttons_layout.addWidget(self.delete_button)
        self.layout.addLayout(buttons_layout)

    def load_task(self, task_id: int | None, lesson_id: int, module_id: int, course_id: int):
        """Загрузка данных задачи"""
        self.current_task_id = task_id
        self.current_lesson_id = lesson_id
        self.current_course_id = course_id
        
        # Получаем module_id из базы данных, если он не передан
        if module_id is None and lesson_id is not None:
            lesson = self.db.get_lesson(lesson_id)
            if lesson:
                module = self.db.get_module_by_lesson(lesson_id)
                if module:
                    self.current_module_id = module['id']
                else:
                    self.current_module_id = None
            else:
                self.current_module_id = None
        else:
            self.current_module_id = module_id

        if task_id:
            task = self.db.get_task(task_id)
            if task:
                self.title_input.setText(task['title'])
                self.file_path_input.setText(task['github_path'] or '')
                self.update_button.setEnabled(True)
                self.delete_button.setEnabled(True)
            else:
                self.clear_form()
        else:
            # Если task_id None, значит создаем новую задачу
            self.clear_form()
            self.update_button.setEnabled(False)
            self.delete_button.setEnabled(False)

    def clear_form(self):
        """Очистка формы"""
        self.current_task_id = None
        # Не очищаем current_lesson_id, current_module_id и current_course_id, так как они должны сохраняться
        self.title_input.clear()
        self.file_path_input.clear()
        self.update_button.setEnabled(False)
        self.delete_button.setEnabled(False)

    def browse_file(self):
        """Выбор файла решения"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл решения",
            "",
            "Markdown Files (*.md);;All Files (*.*)"
        )
        if file_path:
            self.file_path_input.setText(file_path)

    def create_task(self):
        """Создание новой задачи"""
        if not self.current_lesson_id:
            QMessageBox.warning(self, "Ошибка", "Не выбран урок для создания задачи")
            return

        title = self.title_input.text().strip()
        file_path = self.file_path_input.text().strip()

        if not title:
            QMessageBox.warning(self, "Ошибка", "Название задачи не может быть пустым")
            return

        if not file_path:
            QMessageBox.warning(self, "Ошибка", "Не выбран файл решения")
            return

        # Проверяем уникальность названия задачи внутри модуля
        tasks = self.db.get_tasks(self.current_lesson_id)
        for task in tasks:
            if task['title'].lower() == title.lower():
                QMessageBox.warning(self, "Ошибка", "Задача с таким названием уже существует в этом модуле")
                return

        try:
            # Читаем содержимое файла
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            lesson = self.db.get_lesson(self.current_lesson_id)
            course = self.db.get_course(self.current_course_id)
            if not lesson or not course:
                raise ValueError("Урок или курс не найден")

            # Создаем задачу в GitHub
            repo = self.github_api.github.get_repo(f"{self.github_api.user.login}/{course['github_path']}")
            # Получаем путь к директории модуля
            module = self.db.get_module(self.current_module_id)
            if not module:
                raise ValueError("Модуль не найден")
            # Создаем путь для задачи в директории модуля
            task_path = f"{module['github_path']}/{title}.md"
            # Создаем файл в GitHub
            result = repo.create_file(
                task_path,
                f"Add task: {title}",
                content
            )
            raw_url = result['content'].download_url
            
            # Создаем задачу в локальной БД
            task_id = self.db.add_task(
                lesson_id=self.current_lesson_id,
                github_path=task_path,
                title=title,
                raw_url=raw_url
            )

            QMessageBox.information(self, "Успех", "Задача успешно создана")
            # Загружаем созданную задачу
            self.load_task(task_id, self.current_lesson_id, self.current_module_id, self.current_course_id)
            self.task_selected.emit(task_id)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать задачу: {str(e)}")

    def update_task(self):
        """Обновление задачи"""
        if not self.current_task_id:
            QMessageBox.warning(self, "Ошибка", "Не выбран задача для обновления")
            return

        title = self.title_input.text().strip()
        file_path = self.file_path_input.text().strip()

        if not title:
            QMessageBox.warning(self, "Ошибка", "Название задачи не может быть пустым")
            return

        # Проверяем, что название не изменилось
        task = self.db.get_task(self.current_task_id)
        if task and task['title'] != title:
            QMessageBox.warning(self, "Ошибка", "Название задачи нельзя изменить")
            return

        # Проверяем, что выбран новый файл
        if not file_path or file_path == task['github_path']:
            QMessageBox.warning(self, "Ошибка", "Выберите новый файл для обновления задачи")
            return

        try:
            # Читаем содержимое файла
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            course = self.db.get_course(self.current_course_id)
            if not course:
                raise ValueError("Курс не найден")

            # Обновляем задачу в GitHub
            repo = self.github_api.github.get_repo(f"{self.github_api.user.login}/{course['github_path']}")
            try:
                # Получаем содержимое файла для получения SHA
                contents = repo.get_contents(task['github_path'])
                if isinstance(contents, list):
                    # Если это список (директория), берем первый элемент
                    contents = contents[0]
                # Обновляем файл
                repo.update_file(
                    task['github_path'],
                    f"Update task: {title}",
                    content,
                    contents.sha
                )
            except Exception as e:
                raise Exception(f"Не удалось обновить файл в GitHub: {str(e)}")

            # Обновляем задачу в локальной БД
            self.db.update_task(
                self.current_task_id,
                title=title,
                github_path=task['github_path']
            )

            QMessageBox.information(self, "Успех", "Задача успешно обновлена")
            self.task_selected.emit(self.current_task_id)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось обновить задачу: {str(e)}")

    def delete_task(self):
        """Удаление текущей задачи"""
        if not self.current_task_id:
            QMessageBox.warning(self, "Ошибка", "Не выбрана задача для удаления")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить эту задачу?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                task = self.db.get_task(self.current_task_id)
                course = self.db.get_course(self.current_course_id)
                if task and course and task.get('github_path'):
                    # Удаляем задачу из GitHub
                    repo = self.github_api.github.get_repo(f"{self.github_api.user.login}/{course['github_path']}")
                    try:
                        # Получаем содержимое файла для получения SHA
                        contents = repo.get_contents(task['github_path'])
                        if isinstance(contents, list):
                            # Если это список (директория), берем первый элемент
                            contents = contents[0]
                        # Удаляем файл
                        repo.delete_file(
                            task['github_path'],
                            f"Delete task: {task['title']}",
                            contents.sha
                        )
                    except Exception as e:
                        # Если файл не найден, возможно он уже удален
                        print(f"Warning: Could not get file contents: {str(e)}")
                
                # Удаляем задачу из локальной БД
                self.db.delete_task(self.current_task_id)
                
                QMessageBox.information(self, "Успех", "Задача успешно удалена")
                self.clear_form()
                # Отправляем сигнал об удалении задачи
                self.task_deleted.emit()
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить задачу: {str(e)}")
