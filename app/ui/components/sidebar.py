from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTreeView, QPushButton,
                             QLabel, QSizePolicy)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QPixmap, QStandardItemModel, QStandardItem

from app.database.database import Database

class Sidebar(QWidget):
    item_selected = pyqtSignal(str, object)  # Сигнал: тип элемента, id элемента (может быть None)

    def __init__(self):
        super().__init__()
        self.setMinimumWidth(250)
        self.setMaximumWidth(300)
        
        # Инициализируем базу данных
        self.db = Database()
        
        # Создаем основной layout
        layout = QVBoxLayout(self)
        layout.setSpacing(0)  # Убираем отступы между элементами
        layout.setContentsMargins(10, 10, 10, 20)
        
        # Добавляем логотип
        logo_label = QLabel()
        logo_pixmap = QPixmap("app/ui/assets/logo.png")  # TODO: Добавить логотип
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(200, 100, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            logo_label.setText("<h1>КМПО РАНХиГС</h1>")
            logo_label.setMargin(10)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_label)
        
        # Добавляем отступ после логотипа
        layout.addSpacing(20)
        
        # Создаем древовидное представление
        self.tree_view = QTreeView()
        self.tree_view.setModel(self._create_courses_model())
        self.tree_view.clicked.connect(self._handle_item_click)
        self.tree_view.expandAll()  # Раскрываем все элементы по умолчанию
        
        # Настройки для корректной работы прокрутки
        self.tree_view.setVerticalScrollMode(QTreeView.ScrollMode.ScrollPerPixel)  # Плавная прокрутка
        self.tree_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)  # Горизонтальная прокрутка при необходимости
        self.tree_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)  # Вертикальная прокрутка при необходимости
        self.tree_view.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)  # Растягивание по вертикали
        
        layout.addWidget(self.tree_view)
        
        # Добавляем отступ перед кнопками
        layout.addSpacing(20)
        
        # Создаем контейнер для кнопок
        buttons_widget = QWidget()
        buttons_layout = QVBoxLayout(buttons_widget)
        buttons_layout.setSpacing(10)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        
        # Добавляем кнопки
        self.analysis_button = QPushButton("Анализ")
        self.settings_button = QPushButton("Настройки")
        self.settings_button.clicked.connect(self.handle_settings_click)
        
        buttons_layout.addWidget(self.analysis_button)
        buttons_layout.addWidget(self.settings_button)
        
        # Добавляем контейнер с кнопками в основной layout
        layout.addWidget(buttons_widget)
    
    def _handle_item_click(self, index):
        """Обработка клика по элементу дерева"""
        item = self.tree_view.model().itemFromIndex(index)
        if item and item.data():
            item_type, item_id = item.data()
            self.item_selected.emit(item_type, item_id)
    
    def _create_courses_model(self) -> QStandardItemModel:
        """
        Создает модель данных для древовидной структуры курсов из базы данных
        """
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["Структура курсов"])
        
        # Получаем все курсы
        courses = self.db.get_courses()
        
        for course in courses:
            # Создаем элемент курса
            course_item = QStandardItem(course['title'])
            course_item.setEditable(False)
            course_item.setData(("course", course['id']))
            
            # Получаем модули для курса
            modules = self.db.get_modules_by_course(course['id'])
            
            for module in modules:
                # Создаем элемент модуля
                module_item = QStandardItem(module['title'])
                module_item.setEditable(False)
                module_item.setData(("module", module['id']))
                
                # Получаем уроки для модуля
                lessons = self.db.get_lessons_by_module(module['id'])
                
                for lesson in lessons:
                    # Создаем элемент урока
                    lesson_item = QStandardItem(lesson['title'])
                    lesson_item.setEditable(False)
                    lesson_item.setData(("lesson", lesson['id']))
                    
                    # Получаем задачи для урока
                    tasks = self.db.get_tasks_by_lesson(lesson['id'])
                    
                    for task in tasks:
                        # Создаем элемент задачи
                        task_item = QStandardItem(task['title'])
                        task_item.setEditable(False)
                        task_item.setData(("task", task['id']))
                        lesson_item.appendRow(task_item)
                    
                    module_item.appendRow(lesson_item)
                
                course_item.appendRow(module_item)
            
            model.appendRow(course_item)
        
        return model
    
    def refresh(self):
        """Обновление дерева"""
        self.tree_view.setModel(self._create_courses_model())
        self.tree_view.expandAll()

    def handle_settings_click(self):
        """Обработка клика по кнопке настроек"""
        self.item_selected.emit("settings", None)
