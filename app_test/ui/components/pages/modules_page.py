from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTextEdit, QMessageBox
)
from PyQt6.QtCore import pyqtSignal
from app_test.database.local_db import LocalCourseDB
from app_test.api.github_api import GitHubCourseManager


class ModulesPage(QWidget):
    module_selected = pyqtSignal(int)  # Сигнал для выбора модуля
    lesson_creation_requested = pyqtSignal(int)  # Сигнал для создания урока
    module_deleted = pyqtSignal()  # Сигнал для обновления боковой панели после удаления модуля

    def __init__(self, db: LocalCourseDB, github_api: GitHubCourseManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.github_api = github_api
        self.current_module_id = None
        self.current_course_id = None
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        # Заголовок
        self.title_label = QLabel("Модули")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        # Форма модуля
        form_layout = QVBoxLayout()
        
        # Название
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("Название:"))
        self.title_input = QLineEdit()
        title_layout.addWidget(self.title_input)
        form_layout.addLayout(title_layout)

        # Описание
        form_layout.addWidget(QLabel("Описание:"))
        self.description_input = QTextEdit()
        form_layout.addWidget(self.description_input)

        self.layout.addLayout(form_layout)
        self.layout.addStretch()

        # Кнопки управления (внизу)
        buttons_layout = QHBoxLayout()
        self.create_button = QPushButton("Создать модуль")
        self.create_button.clicked.connect(self.create_module)
        self.delete_button = QPushButton("Удалить модуль")
        self.delete_button.clicked.connect(self.delete_module)
        self.create_lesson_button = QPushButton("Создать урок")
        self.create_lesson_button.clicked.connect(self.create_lesson)
        self.create_lesson_button.setEnabled(False)  # По умолчанию отключена

        buttons_layout.addWidget(self.create_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.create_lesson_button)
        self.layout.addLayout(buttons_layout)

    def load_module(self, module_id: int | None, course_id: int):
        """Загрузка данных модуля"""
        self.current_module_id = module_id
        self.current_course_id = course_id
        if module_id:
            module = self.db.get_module(module_id)
            if module:
                self.title_input.setText(module['title'])
                self.description_input.setText(module['description'] or '')
                self.create_lesson_button.setEnabled(True)
                self.delete_button.setEnabled(True)
            else:
                self.clear_form()
        else:
            # Если module_id None, значит создаем новый модуль
            self.clear_form()
            self.create_lesson_button.setEnabled(False)
            self.delete_button.setEnabled(False)

    def clear_form(self):
        """Очистка формы"""
        self.current_module_id = None
        # Не очищаем current_course_id, так как он должен сохраняться
        self.title_input.clear()
        self.description_input.clear()
        self.create_lesson_button.setEnabled(False)
        self.delete_button.setEnabled(False)

    def create_module(self):
        """Создание нового модуля"""
        if not self.current_course_id:
            QMessageBox.warning(self, "Ошибка", "Не выбран курс для создания модуля")
            return

        title = self.title_input.text().strip()
        description = self.description_input.toPlainText().strip()

        if not title:
            QMessageBox.warning(self, "Ошибка", "Название модуля не может быть пустым")
            return

        # Проверяем уникальность названия модуля внутри курса
        modules = self.db.get_modules(self.current_course_id)
        for module in modules:
            if module['title'].lower() == title.lower():
                QMessageBox.warning(self, "Ошибка", "Модуль с таким названием уже существует в этом курсе")
                return

        try:
            course = self.db.get_course(self.current_course_id)
            if not course:
                raise ValueError("Курс не найден")

            # Создаем модуль в GitHub
            repo = self.github_api.github.get_repo(f"{self.github_api.user.login}/{course['github_path']}")
            module_path = self.github_api.create_module(
                repo,
                title,
                description,
                f"Add module: {title}"
            )
            
            # Создаем модуль в локальной БД
            module_id = self.db.add_module(
                course_id=self.current_course_id,
                github_path=module_path,
                title=title,
                description=description
            )

            QMessageBox.information(self, "Успех", "Модуль успешно создан")
            # Загружаем созданный модуль
            self.load_module(module_id, self.current_course_id)
            self.module_selected.emit(module_id)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать модуль: {str(e)}")

    def delete_module(self):
        """Удаление текущего модуля"""
        if not self.current_module_id:
            QMessageBox.warning(self, "Ошибка", "Не выбран модуль для удаления")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить этот модуль?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                module = self.db.get_module(self.current_module_id)
                course = self.db.get_course(self.current_course_id)
                if module and course and module.get('github_path'):
                    # Удаляем модуль из GitHub
                    repo = self.github_api.github.get_repo(f"{self.github_api.user.login}/{course['github_path']}")
                    try:
                        # Получаем содержимое директории модуля
                        contents = repo.get_contents(module['github_path'])
                        if isinstance(contents, list):
                            # Если это список файлов, удаляем каждый файл
                            for content in contents:
                                repo.delete_file(
                                    content.path,
                                    f"Delete file from module: {module['title']}",
                                    content.sha
                                )
                        else:
                            # Если это один файл, удаляем его
                            repo.delete_file(
                                module['github_path'],
                                f"Delete module: {module['title']}",
                                contents.sha
                            )
                    except Exception as e:
                        # Если файл не найден, возможно он уже удален
                        print(f"Warning: Could not get file contents: {str(e)}")
                
                # Удаляем модуль из локальной БД
                self.db.delete_module(self.current_module_id)
                
                QMessageBox.information(self, "Успех", "Модуль успешно удален")
                self.clear_form()
                # Отправляем сигнал об удалении модуля
                self.module_deleted.emit()
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить модуль: {str(e)}")

    def create_lesson(self):
        """Запрос на создание урока"""
        if self.current_module_id:
            self.lesson_creation_requested.emit(self.current_module_id)
