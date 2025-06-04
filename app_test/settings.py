from PyQt6.QtCore import QSettings


class AppSettings:
    def __init__(self) -> None:
        self.settings = QSettings("GusHubApp", "GushubManager")

    def is_fully_configured(self) -> bool:
        # TODO: Добавить проверку логина и пароля.
        return (
                self.get_github_token() != "" # and
                # self.get_gushub_login() != "" and
                # self.get_gushub_password() != ""
        )

    # GitHub Token
    def get_github_token(self) -> str | None:
        return self.settings.value("github/token", None)

    def set_github_token(self, token: str) -> None:
        self.settings.setValue("github/token", token)

    # Gushub Login
    def get_gushub_login(self) -> str | None:
        return self.settings.value("gushub/login", None)

    def set_gushub_login(self, login: str) -> None:
        self.settings.setValue("gushub/login", login)

    # Gushub Password
    def get_gushub_password(self) -> str | None:
        return self.settings.value("gushub/password", None)

    def set_gushub_password(self, password: str) -> None:
        self.settings.setValue("gushub/password", password)

    # Gushub Token
    def get_gushub_token(self) -> str | None:
        return self.settings.value("gushub/token", None)

    def set_gushub_token(self, token: str) -> None:
        self.settings.setValue("gushub/token", token)

    # Очистка (если нужно)
    def clear(self) -> None:
        self.settings.clear()
