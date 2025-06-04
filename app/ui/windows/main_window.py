from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget
from PyQt6.QtCore import Qt
from app.settings import AppSettings
from app.ui.components.sidebar import Sidebar

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gushub - Главное окно")
        self.setMinimumSize(1024, 768)
        
        # Создаем центральный виджет и layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Добавляем сайдбар
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Создаем контейнер для страниц
        self.content_stack = QStackedWidget()
        
        # Создаем и добавляем страницы
        self.welcome_page = QWidget()
        welcome_layout = QVBoxLayout(self.welcome_page)
        welcome_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Добавляем приветствие
        from PyQt6.QtWidgets import QLabel
        welcome_label = QLabel("Добро пожаловать в Gushub!")
        welcome_layout.addWidget(welcome_label)
        
        # Показываем информацию об авторизации
        settings = AppSettings()
        login = settings.get_gushub_login()
        github_token = settings.get_github_token()
        
        auth_info = QLabel(f"Вы авторизованы как: {login}\nGitHub токен: {github_token[:8]}...")
        welcome_layout.addWidget(auth_info)
        
        # Добавляем страницы в стек
        self.content_stack.addWidget(self.welcome_page)
        
        # Добавляем контейнер страниц в главный layout
        main_layout.addWidget(self.content_stack, stretch=1)
    
    def show_page(self, page_index: int) -> None:
        """
        Показывает страницу по индексу
        """
        self.content_stack.setCurrentIndex(page_index)
    
    def add_page(self, page: QWidget) -> int:
        """
        Добавляет новую страницу и возвращает её индекс
        """
        return self.content_stack.addWidget(page)
