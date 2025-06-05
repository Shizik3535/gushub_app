from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QMessageBox, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal

from app.settings import AppSettings
from app.api.github_api import GitHubAPI


class SettingsPage(QWidget):
    show_courses_page = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.settings = AppSettings()
        self.github_api = GitHubAPI(self.settings.get_github_token())

        # Создаем основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(30)
        
        # Заголовок страницы
        title_label = QLabel("<h1>Настройки</h1>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_layout.addWidget(title_label)
        
        # Фрейм для информации
        info_frame = QFrame()
        info_layout = QVBoxLayout(info_frame)
        info_layout.setContentsMargins(20, 20, 20, 20)
        
        # Информация о текущем пользователе
        self.user_info = QLabel(
            f"<h2><b>Текущий пользователь GitHub:</b> {self.github_api.user.login}</h2>"
            f"<h2><b>Текущий пользователь Gushub:</b> {self.settings.get_gushub_login()}</h2>"
        )
        self.user_info.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.user_info.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        info_layout.addWidget(self.user_info)
        
        main_layout.addWidget(info_frame, 1)  # Растягиваем фрейм с информацией
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        self.logout_button = QPushButton("Выйти")
        self.logout_button.clicked.connect(self.logout)
        
        self.courses_button = QPushButton("Вернуться к курсам")
        self.courses_button.clicked.connect(self.show_courses)
        
        buttons_layout.addWidget(self.logout_button)
        buttons_layout.addWidget(self.courses_button)
        
        main_layout.addLayout(buttons_layout)
    
    def logout(self):
        """Выход из аккаунта"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение выхода")
        msg_box.setText("Вы уверены, что хотите выйти из аккаунта?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        # Устанавливаем русский текст для кнопок
        yes_button = msg_box.button(QMessageBox.StandardButton.Yes)
        yes_button.setText("Да")
        no_button = msg_box.button(QMessageBox.StandardButton.No)
        no_button.setText("Нет")
        
        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            # Сбрасываем все настройки
            self.settings.clear()
            # Закрываем приложение
            self.window().close() 
        
    def show_courses(self):
        """Переход на страницу курсов"""
        self.show_courses_page.emit() 
