from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QMessageBox, QDialog, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from app.database.database import Database
from app.ui.forms.courses_add_form import CreateCourseDialog
from app.ui.forms.modules_add_form import CreateModuleDialog
from app.api.github_api import GitHubAPI
from app.settings import AppSettings

class CoursesPage(QWidget):
    # Сигнал для обновления дерева
    tree_update_needed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.settings = AppSettings()
        self.github_api = GitHubAPI(self.settings.get_github_token())
        self.current_course_id = None
        
        # Создаем основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(30)
        
        # Заголовок страницы
        title_label = QLabel("<h1>Управление курсами</h1>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_layout.addWidget(title_label)
        
        # Фрейм для информации о курсе
        course_frame = QFrame()
        course_layout = QVBoxLayout(course_frame)
        course_layout.setContentsMargins(20, 20, 20, 20)
        
        # Информация о курсе
        self.course_info = QLabel("<h2>Курс не выбран</h2>")
        self.course_info.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.course_info.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        course_layout.addWidget(self.course_info)
        
        main_layout.addWidget(course_frame, 1)  # Растягиваем фрейм с информацией
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)
        
        self.create_course_button = QPushButton("Создать курс")
        self.create_course_button.clicked.connect(self.create_course)
        
        self.delete_course_button = QPushButton("Удалить курс")
        self.delete_course_button.clicked.connect(self.delete_course)
        self.delete_course_button.setEnabled(False)
        
        self.create_module_button = QPushButton("Создать модуль")
        self.create_module_button.clicked.connect(self.create_module)
        self.create_module_button.setEnabled(False)
        
        buttons_layout.addWidget(self.create_course_button)
        buttons_layout.addWidget(self.delete_course_button)
        buttons_layout.addWidget(self.create_module_button)
        
        main_layout.addLayout(buttons_layout)
    
    def set_current_course(self, course_id: int | None):
        """Устанавливает текущий курс и обновляет интерфейс"""
        self.current_course_id = course_id
        
        if course_id is None:
            self.course_info.setText("<h2>Курс не выбран</h2>")
            self.delete_course_button.setEnabled(False)
            self.create_module_button.setEnabled(False)
        else:
            course = self.db.get_course(course_id)
            if course:
                self.course_info.setText(
                    f"<h2><b>Название:</b> {course['title']}</h2>"
                    f"<h2><b>Описание:</b> {course['description'] or 'Нет описания'}</h2>"
                )
                self.delete_course_button.setEnabled(True)
                self.create_module_button.setEnabled(True)
    
    def create_course(self):
        """Создание нового курса"""
        dialog = CreateCourseDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            title, description = dialog.get_course_data()
            if title:  # Проверяем, что название не пустое
                try:
                    # Проверяем, существует ли уже курс с таким названием
                    existing_courses = self.db.get_courses()
                    if any(course['title'].lower() == title.lower() for course in existing_courses):
                        QMessageBox.warning(
                            self,
                            "Предупреждение",
                            "Курс с таким названием уже существует"
                        )
                        return
                    
                    # Создаем репозиторий на GitHub
                    repo = self.github_api.create_course(title, description)
                    
                    # Добавляем курс в базу данных
                    course_id = self.db.add_course(repo.html_url, title, description)
                    self.set_current_course(course_id)
                    # Отправляем сигнал для обновления дерева
                    self.tree_update_needed.emit()
                    
                    # Показываем сообщение об успешном создании
                    QMessageBox.information(
                        self,
                        "Успех",
                        f"Курс '{title}' успешно создан"
                    )
                    
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Ошибка",
                        f"Не удалось создать курс: {str(e)}"
                    )
    
    def delete_course(self):
        """Удаление текущего курса"""
        if self.current_course_id is None:
            return
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение удаления")
        msg_box.setText("Вы уверены, что хотите удалить этот курс?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        # Устанавливаем русский текст для кнопок
        yes_button = msg_box.button(QMessageBox.StandardButton.Yes)
        yes_button.setText("Да")
        no_button = msg_box.button(QMessageBox.StandardButton.No)
        no_button.setText("Нет")
        
        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            try:
                # Получаем информацию о курсе
                course = self.db.get_course(self.current_course_id)
                if course and course['github_path']:
                    # Удаляем репозиторий на GitHub
                    repo_name = course['github_path'].split('/')[-1]
                    self.github_api.delete_course(repo_name)
                
                # Удаляем курс из базы данных
                self.db.delete_course(self.current_course_id)
                self.set_current_course(None)
                # Отправляем сигнал для обновления дерева
                self.tree_update_needed.emit()
                
                # Показываем сообщение об успешном удалении
                QMessageBox.information(
                    self,
                    "Успех",
                    f"Курс '{course['title']}' успешно удален"
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось удалить курс: {str(e)}"
                )
    
    def create_module(self):
        """Создание нового модуля для текущего курса"""
        if self.current_course_id is None:
            return
        
        dialog = CreateModuleDialog(self.current_course_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            title, description = dialog.get_module_data()
            if title:  # Проверяем, что название не пустое
                try:
                    # Получаем информацию о курсе
                    course = self.db.get_course(self.current_course_id)
                    if course and course['github_path']:
                        # Получаем репозиторий курса
                        repo = self.github_api.get_course(course['title'])
                        # Создаем модуль в репозитории
                        module_path = self.github_api.create_module(repo, title, description)
                    
                    # Добавляем модуль в базу данных
                    self.db.add_module(self.current_course_id, module_path, title, description)
                    # Отправляем сигнал для обновления дерева
                    self.tree_update_needed.emit()
                    
                    # Показываем сообщение об успешном создании
                    QMessageBox.information(
                        self,
                        "Успех",
                        f"Модуль '{title}' успешно создан в курсе '{course['title']}'"
                    )
                    
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Ошибка",
                        f"Не удалось создать модуль: {str(e)}"
                    )
