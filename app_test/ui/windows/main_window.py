from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QStackedWidget
)
from PyQt6.QtCore import Qt

from app_test.database.local_db import LocalCourseDB
from app_test.settings import AppSettings
from app_test.ui.components.sidebar import SidebarTree
from app_test.ui.components.pages.courses_page import CoursesPage
from app_test.ui.components.pages.modules_page import ModulesPage
from app_test.ui.components.pages.lessons_page import LessonsPage
from app_test.ui.components.pages.tasks_page import TasksPage
from app_test.api.github_api import GitHubCourseManager


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GusHub")
        self.setMinimumSize(1200, 800)

        self.settings = AppSettings()
        self.db = LocalCourseDB()
        self.github_api = GitHubCourseManager(self.settings.get_github_token())

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной layout
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Создаем боковую панель
        self.sidebar = SidebarTree(db=self.db)
        self.sidebar.setMaximumWidth(300)  # Ограничиваем ширину боковой панели
        self.sidebar.item_selected.connect(self.handle_item_selection)
        layout.addWidget(self.sidebar)

        # Создаем стек для страниц
        self.stack = QStackedWidget()
        layout.addWidget(self.stack)

        # Создаем страницы
        self.courses_page = CoursesPage(self.db, self.github_api)
        self.modules_page = ModulesPage(self.db, self.github_api)
        self.lessons_page = LessonsPage(self.db, self.github_api)
        self.tasks_page = TasksPage(self.db, self.github_api)

        # Добавляем страницы в стек
        self.stack.addWidget(self.courses_page)
        self.stack.addWidget(self.modules_page)
        self.stack.addWidget(self.lessons_page)
        self.stack.addWidget(self.tasks_page)

        # Подключаем сигналы
        self.courses_page.module_creation_requested.connect(self.handle_module_creation)
        self.modules_page.lesson_creation_requested.connect(self.handle_lesson_creation)
        self.lessons_page.task_creation_requested.connect(self.handle_task_creation)

        # Сигналы для обновления боковой панели
        self.courses_page.course_deleted.connect(self.sidebar.refresh)
        self.modules_page.module_deleted.connect(self.sidebar.refresh)
        self.lessons_page.lesson_deleted.connect(self.sidebar.refresh)
        self.tasks_page.task_deleted.connect(self.sidebar.refresh)
        
        # Сигналы для обновления при создании
        self.courses_page.course_selected.connect(self.sidebar.refresh)
        self.modules_page.module_selected.connect(self.sidebar.refresh)
        self.lessons_page.lesson_selected.connect(self.sidebar.refresh)
        self.tasks_page.task_selected.connect(self.sidebar.refresh)

        # Показываем страницу курсов по умолчанию
        self.stack.setCurrentWidget(self.courses_page)

    def setup_connections(self):
        # Подключаем сигналы от боковой панели
        self.sidebar.item_selected.connect(self.handle_item_selection)
        
        # Подключаем сигналы от страницы курсов
        self.courses_page.course_selected.connect(self.handle_course_selection)
        self.courses_page.module_creation_requested.connect(self.handle_module_creation)
        self.courses_page.course_deleted.connect(self.handle_course_deleted)

        # Подключаем сигналы от страницы модулей
        self.modules_page.module_selected.connect(self.handle_module_selection)
        self.modules_page.lesson_creation_requested.connect(self.handle_lesson_creation)
        self.modules_page.module_deleted.connect(self.handle_module_deleted)

        # Подключаем сигналы от страницы уроков
        self.lessons_page.lesson_selected.connect(self.handle_lesson_selection)
        self.lessons_page.task_creation_requested.connect(self.handle_task_creation)
        self.lessons_page.lesson_deleted.connect(self.handle_lesson_deleted)

    def handle_item_selection(self, item_type: str, item_id: int):
        """Обработка выбора элемента в боковой панели"""
        if item_type == "course":
            self.courses_page.load_course(item_id)
            self.stack.setCurrentWidget(self.courses_page)
        elif item_type == "module":
            course = self.db.get_course_by_module(item_id)
            if course:
                self.modules_page.load_module(item_id, course['id'])
                self.stack.setCurrentWidget(self.modules_page)
        elif item_type == "lesson":
            module = self.db.get_module_by_lesson(item_id)
            if module:
                course = self.db.get_course_by_module(module['id'])
                if course:
                    self.lessons_page.load_lesson(item_id, module['id'], course['id'])
                    self.stack.setCurrentWidget(self.lessons_page)
        elif item_type == "task":
            task = self.db.get_task(item_id)
            if task:
                lesson = self.db.get_lesson(task['lesson_id'])
                if lesson:
                    module = self.db.get_module_by_lesson(lesson['id'])
                    if module:
                        course = self.db.get_course(module['course_id'])
                        if course:
                            self.tasks_page.load_task(item_id, lesson['id'], module['id'], course['id'])
                            self.stack.setCurrentWidget(self.tasks_page)
        # TODO: Добавить обработку других типов элементов (уроки, задачи)

    def handle_course_selection(self, course_id: int):
        """Обработка выбора курса"""
        self.sidebar.refresh()  # Обновляем боковую панель

    def handle_module_creation(self, course_id: int):
        """Обработка запроса на создание модуля"""
        self.modules_page.current_course_id = course_id
        self.modules_page.load_module(None, course_id)
        self.stack.setCurrentWidget(self.modules_page)

    def handle_module_selection(self, module_id: int):
        """Обработка выбора модуля"""
        self.sidebar.refresh()  # Обновляем боковую панель

    def handle_lesson_creation(self, module_id: int):
        """Обработка запроса на создание урока"""
        course = self.db.get_course_by_module(module_id)
        if course:
            self.lessons_page.load_lesson(None, module_id, course['id'])
            self.stack.setCurrentWidget(self.lessons_page)

    def handle_lesson_selection(self, lesson_id: int):
        """Обработка выбора урока"""
        self.sidebar.refresh()  # Обновляем боковую панель

    def handle_task_creation(self, lesson_id: int):
        """Обработка запроса на создание задачи"""
        module = self.db.get_module_by_lesson(lesson_id)
        if module:
            course = self.db.get_course(module['course_id'])
            if course:
                self.tasks_page.load_task(None, lesson_id, module['id'], course['id'])
                self.stack.setCurrentWidget(self.tasks_page)

    def handle_module_deleted(self):
        """Обработка удаления модуля"""
        self.sidebar.refresh()  # Обновляем боковую панель

    def handle_course_deleted(self):
        """Обработка удаления курса"""
        self.sidebar.refresh()  # Обновляем боковую панель

    def handle_lesson_deleted(self):
        """Обработка удаления урока"""
        self.sidebar.refresh()  # Обновляем боковую панель

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        self.db.close()
        event.accept()
