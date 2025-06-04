from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtCore import Qt
from app.settings import AppSettings
from app.ui.windows.main_window import MainWindow

class AuthWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gushub - Авторизация")
        self.setFixedSize(400, 300)
        
        # Создаем центральный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Поля ввода
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин Gushub")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль Gushub")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.github_token_input = QLineEdit()
        self.github_token_input.setPlaceholderText("GitHub Token")
        self.github_token_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        # Кнопка авторизации
        self.auth_button = QPushButton("Войти")
        self.auth_button.clicked.connect(self.handle_auth)
        
        # Добавляем виджеты на форму
        layout.addWidget(QLabel("Авторизация в Gushub"))
        layout.addWidget(self.login_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.github_token_input)
        layout.addWidget(self.auth_button)
        
        # Добавляем отступы
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
    
    def validate_gushub_credentials(self, login: str, password: str) -> bool:
        """
        Валидация учетных данных Gushub
        TODO: Реализовать реальную валидацию
        """
        return True
    
    def validate_github_token(self, token: str) -> bool:
        """
        Валидация GitHub токена
        """
        # TODO: Реализовать проверку токена через GitHub API
        return bool(token and len(token) > 0)
    
    def handle_auth(self):
        login = self.login_input.text()
        password = self.password_input.text()
        github_token = self.github_token_input.text()
        
        if not login or not password or not github_token:
            QMessageBox.warning(self, "Ошибка", "Все поля должны быть заполнены")
            return
        
        if not self.validate_gushub_credentials(login, password):
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")
            return
        
        if not self.validate_github_token(github_token):
            QMessageBox.warning(self, "Ошибка", "Неверный GitHub токен")
            return
        
        # Сохраняем данные в настройках
        settings = AppSettings()
        settings.set_gushub_credentials(login, password)
        settings.set_github_token(github_token)
        
        QMessageBox.information(self, "Успех", "Авторизация успешна")
        
        # Создаем и показываем главное окно
        self.main_window = MainWindow()
        self.main_window.show()
        
        # Закрываем окно авторизации
        self.close()
