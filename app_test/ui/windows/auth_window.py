from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox
)

from app_test.settings import AppSettings


class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация")
        self.setFixedSize(300, 200)

        self.settings = AppSettings()

        layout = QVBoxLayout()

        # Логин
        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин Gushub")
        layout.addWidget(QLabel("Логин:"))
        layout.addWidget(self.login_input)

        # Пароль
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Пароль Gushub")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("Пароль:"))
        layout.addWidget(self.password_input)

        # GitHub Token
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("GitHub Token")
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(QLabel("GitHub Token:"))
        layout.addWidget(self.token_input)

        # Сохранить
        self.save_button = QPushButton("Войти")
        self.save_button.clicked.connect(self.save_credentials)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_credentials(self):
        login = self.login_input.text().strip()
        password = self.password_input.text().strip()
        token = self.token_input.text().strip()

        # Сохраняем в QSettings
        self.settings.set_gushub_login(login)
        self.settings.set_gushub_password(password)
        self.settings.set_github_token(token)

        QMessageBox.information(self, "Успех", "Данные сохранены.")
        self.close()
