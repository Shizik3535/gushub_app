from PyQt6.QtWidgets import QApplication
import sys
from qt_material import apply_stylesheet

from app_test.settings import AppSettings
from app_test.ui.windows.auth_window import AuthWindow
from app_test.ui.windows.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    apply_stylesheet(app, theme="dark_red.xml")
    settings = AppSettings()

    if settings.is_fully_configured():
        window = MainWindow()
    else:
        window = AuthWindow()

    window.show()
    sys.exit(app.exec())
