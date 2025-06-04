from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QLineEdit, QTextEdit, QMessageBox
)
from PyQt6.QtCore import pyqtSignal
from app_test.database.local_db import LocalCourseDB
from app_test.api.github_api import GitHubCourseManager


class CoursesPage(QWidget):
    course_selected = pyqtSignal(int)  # Сигнал для выбора курса
    module_creation_requested = pyqtSignal(int)  # Сигнал для создания модуля
    course_deleted = pyqtSignal()  # Сигнал для обновления боковой панели после удаления курса

    def __init__(self, db: LocalCourseDB, github_api: GitHubCourseManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.github_api = github_api
        self.current_course_id = None
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout(self)

        # Заголовок
        self.title_label = QLabel("Курсы")
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.layout.addWidget(self.title_label)

        # Форма курса
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
        self.create_button = QPushButton("Создать курс")
        self.create_button.clicked.connect(self.create_course)
        self.delete_button = QPushButton("Удалить курс")
        self.delete_button.clicked.connect(self.delete_course)
        self.create_module_button = QPushButton("Создать модуль")
        self.create_module_button.clicked.connect(self.create_module)
        self.create_module_button.setEnabled(False)  # По умолчанию отключена

        buttons_layout.addWidget(self.create_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.create_module_button)
        self.layout.addLayout(buttons_layout)

    def load_course(self, course_id: int):
        """Загрузка данных курса"""
        self.current_course_id = course_id
        course = self.db.get_course(course_id)
        if course:
            self.title_input.setText(course['title'])
            self.description_input.setText(course['description'] or '')
            self.create_module_button.setEnabled(True)
        else:
            self.clear_form()

    def clear_form(self):
        """Очистка формы"""
        self.current_course_id = None
        self.title_input.clear()
        self.description_input.clear()
        self.create_module_button.setEnabled(False)

    def create_course(self):
        """Создание нового курса"""
        title = self.title_input.text().strip()
        description = self.description_input.toPlainText().strip()

        if not title:
            QMessageBox.warning(self, "Ошибка", "Название курса не может быть пустым")
            return

        # Проверяем уникальность названия курса
        courses = self.db.get_courses()
        for course in courses:
            if course['title'].lower() == title.lower():
                QMessageBox.warning(self, "Ошибка", "Курс с таким названием уже существует")
                return

        try:
            # Создаем курс в GitHub
            repo = self.github_api.github.get_repo(f"{self.github_api.user.login}/{title}")
            course_path = self.github_api.create_course(
                repo, 
                title, 
                "",  # Пустое содержимое, так как курс - это контейнер
                f"Add course: {title}"
            )
            
            # Создаем курс в локальной БД
            course_id = self.db.add_course(
                github_path=course_path,
                title=title,
                description=description,
                raw_url=course_path
            )

            QMessageBox.information(self, "Успех", "Курс успешно создан")
            self.course_selected.emit(course_id)
            
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось создать курс: {str(e)}")

    def delete_course(self):
        """Удаление текущего курса"""
        if not self.current_course_id:
            QMessageBox.warning(self, "Ошибка", "Не выбран курс для удаления")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить этот курс?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                course = self.db.get_course(self.current_course_id)
                if course and course.get('github_path'):
                    # Удаляем репозиторий из GitHub
                    repo = self.github_api.github.get_repo(f"{self.github_api.user.login}/{course['github_path']}")
                    repo.delete()
                
                # Удаляем курс из локальной БД
                self.db.delete_course(self.current_course_id)
                
                QMessageBox.information(self, "Успех", "Курс успешно удален")
                self.clear_form()
                # Отправляем сигнал об удалении курса
                self.course_deleted.emit()
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось удалить курс: {str(e)}")

    def create_module(self):
        """Запрос на создание модуля"""
        if not self.current_course_id:
            QMessageBox.warning(self, "Ошибка", "Не выбран курс для создания модуля")
            return
        self.module_creation_requested.emit(self.current_course_id)
