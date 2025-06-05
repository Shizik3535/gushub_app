from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QTextEdit, QPushButton, QMessageBox,
                             QFileDialog)
from PyQt6.QtCore import Qt

class CreateTaskDialog(QDialog):
    def __init__(self, lesson_id: int, parent=None):
        super().__init__(parent)
        self.lesson_id = lesson_id
        self.setWindowTitle("Создание задачи")
        self.setMinimumWidth(400)
        
        # Создаем layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Поле для названия
        title_layout = QVBoxLayout()
        title_label = QLabel("Название задачи:")
        self.title_edit = QLineEdit()
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_edit)
        layout.addLayout(title_layout)
        
        # Поле для выбора файла
        file_layout = QVBoxLayout()
        file_label = QLabel("Файл с задачей:")
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setPlaceholderText("Выберите файл с задачей...")
        select_file_button = QPushButton("Выбрать файл")
        select_file_button.clicked.connect(self.select_file)
        
        file_buttons_layout = QHBoxLayout()
        file_buttons_layout.addWidget(self.file_path_edit)
        file_buttons_layout.addWidget(select_file_button)
        
        file_layout.addWidget(file_label)
        file_layout.addLayout(file_buttons_layout)
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
        """Выбор файла с задачей"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл с задачей",
            "",
            "Markdown Files (*.md);;All Files (*.*)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
    
    def get_task_data(self) -> tuple[str, str]:
        """Возвращает данные задачи"""
        return self.title_edit.text().strip(), self.file_path_edit.text().strip() 