from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QFileDialog)
from PyQt6.QtCore import Qt

class UpdateTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Обновление задачи")
        self.setMinimumWidth(400)
        
        # Создаем layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Поле для выбора файла
        file_layout = QVBoxLayout()
        file_label = QLabel("Новый файл с задачей:")
        self.file_path_edit = QLineEdit()
        self.file_path_edit.setReadOnly(True)
        self.file_path_edit.setPlaceholderText("Выберите новый файл с задачей...")
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
        self.update_button = QPushButton("Обновить")
        self.update_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Отмена")
        self.cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(self.update_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)
    
    def select_file(self):
        """Выбор файла с задачей"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите новый файл с задачей",
            "",
            "Markdown Files (*.md);;All Files (*.*)"
        )
        if file_path:
            self.file_path_edit.setText(file_path)
    
    def get_file_path(self) -> str:
        """Возвращает путь к выбранному файлу"""
        return self.file_path_edit.text().strip()
