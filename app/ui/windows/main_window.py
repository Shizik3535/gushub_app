from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt
from app.settings import AppSettings
from app.ui.components.sidebar import Sidebar
from app.ui.pages.courses_page import CoursesPage

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
        self.sidebar.item_selected.connect(self.handle_item_selection)
        
        # Создаем контейнер для основного контента
        self.content_stack = QStackedWidget()
        
        # Создаем страницу курсов
        self.courses_page = CoursesPage()
        self.courses_page.tree_update_needed.connect(self.sidebar.refresh)
        self.content_stack.addWidget(self.courses_page)
        
        # Добавляем виджеты в layout
        layout.addWidget(self.sidebar)
        layout.addWidget(self.content_stack)
        
        # Устанавливаем пропорции layout
        layout.setStretch(0, 1)  # Сайдбар
        layout.setStretch(1, 4)  # Контент
    
    def handle_item_selection(self, item_type: str, item_id: int):
        """Обработка выбора элемента в сайдбаре"""
        if item_type == "course":
            self.courses_page.set_current_course(item_id)
        else:
            self.courses_page.set_current_course(None)
