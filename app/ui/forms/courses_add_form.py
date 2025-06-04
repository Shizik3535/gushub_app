from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QTextEdit, QHBoxLayout, QPushButton

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
        
        # Добавляем поля в форму
        layout.addRow("Название:", self.title_input)
        layout.addRow("Описание:", self.description_input)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        self.create_button = QPushButton("Создать")
        self.cancel_button = QPushButton("Отмена")
        
        self.create_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.create_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addRow("", buttons_layout)
    
    def get_course_data(self) -> tuple[str, str]:
        """Возвращает введенные данные о курсе"""
        return self.title_input.text(), self.description_input.toPlainText()
