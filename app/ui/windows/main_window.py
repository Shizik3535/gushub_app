from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from app.settings import AppSettings
from app.ui.components.sidebar import Sidebar
from app.ui.pages.courses_page import CoursesPage
from app.ui.pages.modules_page import ModulesPage
from app.ui.pages.lessons_page import LessonsPage
from app.ui.pages.tasks_page import TasksPage
from app.ui.pages.settings_page import SettingsPage
from app.ui.pages.analytics_page import AnalyticsPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gushub")
        self.setMinimumSize(1200, 800)
        
        # Создаем центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Создаем горизонтальный layout
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Создаем сайдбар
        self.sidebar = Sidebar()
        
        # Создаем контейнер для основного контента
        self.content_stack = QStackedWidget()
        
        # Создаем страницу курсов
        self.courses_page = CoursesPage()
        self.courses_page.tree_update_needed.connect(self.sidebar.refresh)
        self.content_stack.addWidget(self.courses_page)
        
        # Создаем страницу модулей
        self.modules_page = ModulesPage()
        self.modules_page.tree_update_needed.connect(self.sidebar.refresh)
        self.content_stack.addWidget(self.modules_page)
        
        # Создаем страницу уроков
        self.lessons_page = LessonsPage()
        self.lessons_page.tree_update_needed.connect(self.sidebar.refresh)
        self.content_stack.addWidget(self.lessons_page)

        # Создаем страницу заданий
        self.tasks_page = TasksPage()
        self.tasks_page.tree_update_needed.connect(self.sidebar.refresh)
        self.content_stack.addWidget(self.tasks_page)

        # Создаем страницу настроек
        self.settings_page = SettingsPage()
        self.content_stack.addWidget(self.settings_page)
        
        # Создаем страницу аналитики
        self.analytics_page = AnalyticsPage()
        self.analytics_page.show_courses_page.connect(self.show_courses_page)
        self.content_stack.addWidget(self.analytics_page)
        
        # Добавляем виджеты в layout
        layout.addWidget(self.sidebar)
        layout.addWidget(self.content_stack)
        
        # Устанавливаем пропорции layout
        layout.setStretch(0, 1)  # Сайдбар
        layout.setStretch(1, 4)  # Контент
        
        # Подключаем сигналы
        self.sidebar.item_selected.connect(self.handle_item_selection)
        self.settings_page.show_courses_page.connect(self.show_courses_page)
        self.courses_page.tree_update_needed.connect(self.sidebar.refresh)
        self.modules_page.tree_update_needed.connect(self.sidebar.refresh)
        self.lessons_page.tree_update_needed.connect(self.sidebar.refresh)
        self.tasks_page.tree_update_needed.connect(self.sidebar.refresh)
        self.courses_page.module_selected.connect(self.handle_module_selection)
    
    def handle_item_selection(self, item_type: str, item_id: int | None):
        """Обработка выбора элемента в боковой панели"""
        if item_type == "course":
            # Показываем страницу курсов
            self.courses_page.set_current_course(item_id)
            self.content_stack.setCurrentWidget(self.courses_page)
        elif item_type == "module":
            # Показываем страницу модулей
            self.modules_page.set_current_module(item_id)
            self.content_stack.setCurrentWidget(self.modules_page)
        elif item_type == "lesson":
            # Показываем страницу уроков
            self.lessons_page.set_current_lesson(item_id)
            self.content_stack.setCurrentWidget(self.lessons_page)
        elif item_type == "task":
            # Показываем страницу заданий
            self.tasks_page.set_current_task(item_id)
            self.content_stack.setCurrentWidget(self.tasks_page)
        elif item_type == "settings":
            # Показываем страницу настроек
            self.content_stack.setCurrentWidget(self.settings_page)
        elif item_type == "analytics":
            # Показываем страницу аналитики
            self.content_stack.setCurrentWidget(self.analytics_page)
        else:
            # Скрываем все страницы
            self.courses_page.set_current_course(None)
            self.modules_page.set_current_module(None)
            self.lessons_page.set_current_lesson(None)
            self.tasks_page.set_current_task(None)

    def handle_module_selection(self, module_id: int):
        """Обработка выбора модуля после его создания"""
        self.modules_page.set_current_module(module_id)
        self.content_stack.setCurrentWidget(self.modules_page)

    def show_courses_page(self):
        """Показывает страницу курсов"""
        self.courses_page.set_current_course(None)
        self.content_stack.setCurrentWidget(self.courses_page)