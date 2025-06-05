from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt

class AnalyticsPage(QWidget):
    def __init__(self):
        super().__init__()
        
        # Создаем основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Добавляем заголовок
        title = QLabel("Аналитика")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Добавляем заглушку
        placeholder = QLabel("Здесь будет отображаться аналитика")
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(placeholder)
        
        # Добавляем растягивающийся элемент
        layout.addStretch()
