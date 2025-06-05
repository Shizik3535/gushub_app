from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QLineEdit, QFileDialog)
from PyQt6.QtCore import Qt
import os

class CreateLessonDialog(QDialog):
    def __init__(self, module_id: int, parent=None):
        super().__init__(parent)
        self.module_id = module_id
        self.title = ""
        self.file_path = ""
        
        self.setWindowTitle("Создание урока")
        self.setMinimumWidth(400)
        
        # Создаем layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Поле для названия
        title_layout = QVBoxLayout()
        title_label = QLabel("Название урока:")
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Введите название урока")
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_input)
        layout.addLayout(title_layout)
        
        # Поле для выбора файла
        file_layout = QVBoxLayout()
        file_label = QLabel("Файл урока (.md):")
        self.file_path_label = QLabel("Файл не выбран")
        self.select_file_button = QPushButton("Выбрать файл")
        self.select_file_button.clicked.connect(self.select_file)
        file_layout.addWidget(file_label)
        file_layout.addWidget(self.file_path_label)
        file_layout.addWidget(self.select_file_button)
        layout.addLayout(file_layout)
        
        # Кнопки
        buttons_layout = QHBoxLayout()

        self.create_button = QPushButton("Создать")
        self.create_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.create_button)
        buttons_layout.addWidget(self.cancel_button)
        
        layout.addLayout(buttons_layout)
    
    def select_file(self):
        """Открывает диалог выбора файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл урока",
            "",
            "Markdown Files (*.md)"
        )
        if file_path:
            self.file_path = file_path
            self.file_path_label.setText(os.path.basename(file_path))
    
    def get_lesson_data(self) -> tuple[str, str]:
        """Возвращает введенные данные урока"""
        return self.title_input.text().strip(), self.file_path
