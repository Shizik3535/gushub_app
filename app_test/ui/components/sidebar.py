from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeView
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import pyqtSignal
from app_test.database.local_db import LocalCourseDB
from typing import Optional


class SidebarTree(QWidget):
    item_selected = pyqtSignal(str, int)  # Сигнал: тип элемента, id элемента

    def __init__(self, db: Optional[LocalCourseDB] = None, parent=None):
        super().__init__(parent)
        self.db = db or LocalCourseDB()

        self.layout = QVBoxLayout(self)
        self.tree_view = QTreeView()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Структура курсов"])

        self.tree_view.setModel(self.model)
        self.tree_view.clicked.connect(self.handle_item_click)
        self.layout.addWidget(self.tree_view)

        self.populate_tree()

    def handle_item_click(self, index):
        """Обработка клика по элементу дерева"""
        item = self.model.itemFromIndex(index)
        if item and item.data():
            item_type, item_id = item.data()
            self.item_selected.emit(item_type, item_id)

    def populate_tree(self):
        """Заполнение дерева данными"""
        self.model.removeRows(0, self.model.rowCount())
        courses = self.db.get_all_courses()

        for course in courses:
            course_item = QStandardItem(course["title"])
            course_item.setEditable(False)
            course_item.setData(("course", course["id"]))

            modules = self.db.get_modules(course["id"])
            for module in modules:
                module_item = QStandardItem(module["title"])
                module_item.setEditable(False)
                module_item.setData(("module", module["id"]))

                lessons = self.db.get_lessons(module["id"])
                for lesson in lessons:
                    lesson_item = QStandardItem(f"[Урок] {lesson['title']}")
                    lesson_item.setEditable(False)
                    lesson_item.setData(("lesson", lesson["id"]))

                    tasks = self.db.get_tasks(lesson["id"])
                    for task in tasks:
                        task_item = QStandardItem(f"[Задание] {task['title']}")
                        task_item.setEditable(False)
                        task_item.setData(("task", task["id"]))
                        lesson_item.appendRow(task_item)

                    module_item.appendRow(lesson_item)

                course_item.appendRow(module_item)

            self.model.appendRow(course_item)

    def refresh(self):
        """Обновление дерева"""
        self.populate_tree()
