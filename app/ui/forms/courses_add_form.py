from PyQt6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QTextEdit, 
                             QHBoxLayout, QPushButton, QFileDialog, QLabel)
from PyQt6.QtCore import Qt
import os

class CreateCourseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Создание курса")
        self.setMinimumWidth(400)
        
        layout = QFormLayout(self)
        
        # Поля ввода
        self.title_input = QLineEdit()
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(100)
        
        # Выбор изображения
        image_layout = QHBoxLayout()
        self.image_path_label = QLabel("Изображение не выбрано")
        self.select_image_button = QPushButton("Выбрать")
        self.select_image_button.clicked.connect(self.select_image)
        self.image_path = None
        
        image_layout.addWidget(self.image_path_label)
        image_layout.addWidget(self.select_image_button)
        
        # Добавляем поля в форму
        layout.addRow("Название:", self.title_input)
        layout.addRow("Описание:", self.description_input)
        layout.addRow("Изображение:", image_layout)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        self.create_button = QPushButton("Создать")
        self.cancel_button = QPushButton("Отмена")
        
        self.create_button.clicked.connect(self.validate_and_accept)
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.create_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addRow("", buttons_layout)
    
    def select_image(self):
        """Выбор изображения для курса"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите изображение",
            "",
            "Изображения (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.image_path = file_path
            self.image_path_label.setText(os.path.basename(file_path))
    
    def validate_and_accept(self):
        """Проверка данных перед принятием формы"""
        title = self.title_input.text().strip()
        description = self.description_input.toPlainText().strip()
        
        if not title:
            self.show_error("Введите название курса")
            return
        
        # Проверяем, что описание содержит минимум 3 слова
        if len(description) < 3:
            self.show_error("Описание должно содержать минимум 3 символа")
            return
        
        if not self.image_path:
            self.show_error("Выберите изображение для курса")
            return
        
        self.accept()
    
    def show_error(self, message: str):
        """Показ сообщения об ошибке"""
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.warning(self, "Ошибка", message)
    
    def get_course_data(self) -> tuple[str, str, str]:
        """Возвращает введенные данные о курсе"""
        return (
            self.title_input.text().strip(),
            self.description_input.toPlainText().strip(),
            self.image_path
        )
