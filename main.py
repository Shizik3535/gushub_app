import sys
from PyQt6.QtWidgets import QApplication
from qt_material import apply_stylesheet
from PyQt6.QtGui import QIcon

from app.ui.windows.auth_window import AuthWindow
from app.ui.windows.main_window import MainWindow
from app.settings import AppSettings

def main():
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon("app/ui/assets/icon.ico"))
    apply_stylesheet(app, theme="dark_red.xml")
    
    # Проверяем, авторизован ли пользователь
    settings = AppSettings()
    
    if settings.is_fully_configured():
        # Если авторизован, показываем главное окно
        window = MainWindow()
        window.show()
    else:
        # Если не авторизован, показываем окно авторизации
        auth_window = AuthWindow()
        auth_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
