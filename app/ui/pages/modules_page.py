from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QMessageBox, QDialog, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from app.database.database import Database
from app.ui.forms.lessons_add_form import CreateLessonDialog
from app.api.github_api import GitHubAPI
from app.api.gushub_api import GushubAPI
from app.settings import AppSettings
import urllib.parse

class ModulesPage(QWidget):
    # Сигнал для обновления дерева
    tree_update_needed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.settings = AppSettings()
        self.github_api = GitHubAPI(self.settings.get_github_token())
        self.gushub_api = GushubAPI()
        self.current_module_id = None
        
        # Создаем основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(30)
        
        # Заголовок страницы
        title_label = QLabel("<h1>Управление модулями</h1>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_layout.addWidget(title_label)
        
        # Фрейм для информации о модуле
        module_frame = QFrame()
        module_layout = QVBoxLayout(module_frame)
        module_layout.setContentsMargins(20, 20, 20, 20)
        
        # Информация о модуле
        self.module_info = QLabel("<h2>Модуль не выбран</h2>")
        self.module_info.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.module_info.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        module_layout.addWidget(self.module_info)
        
        main_layout.addWidget(module_frame, 1)  # Растягиваем фрейм с информацией
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        self.delete_module_button = QPushButton("Удалить модуль")
        self.delete_module_button.clicked.connect(self.delete_module)
        self.delete_module_button.setEnabled(False)
        
        self.create_lesson_button = QPushButton("Создать урок")
        self.create_lesson_button.clicked.connect(self.create_lesson)
        self.create_lesson_button.setEnabled(False)
        
        buttons_layout.addWidget(self.delete_module_button)
        buttons_layout.addWidget(self.create_lesson_button)
        
        main_layout.addLayout(buttons_layout)
    
    def set_current_module(self, module_id: int | None):
        """Устанавливает текущий модуль и обновляет интерфейс"""
        self.current_module_id = module_id
        
        if module_id is None:
            self.module_info.setText("<h2>Модуль не выбран</h2>")
            self.delete_module_button.setEnabled(False)
            self.create_lesson_button.setEnabled(False)
        else:
            module = self.db.get_module(module_id)
            if module:
                self.module_info.setText(
                    f"<h2><b>Название:</b> {module['title']}</h2>"
                    f"<h2><b>Описание:</b> {module['description'] or 'Нет описания'}</h2>"
                )
                self.delete_module_button.setEnabled(True)
                self.create_lesson_button.setEnabled(True)
    
    def delete_module(self):
        """Удаление текущего модуля"""
        if self.current_module_id is None:
            return
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение удаления")
        msg_box.setText("Вы уверены, что хотите удалить этот модуль?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        # Устанавливаем русский текст для кнопок
        yes_button = msg_box.button(QMessageBox.StandardButton.Yes)
        yes_button.setText("Да")
        no_button = msg_box.button(QMessageBox.StandardButton.No)
        no_button.setText("Нет")
        
        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            try:
                # Получаем информацию о модуле
                module = self.db.get_module(self.current_module_id)
                if module:
                    # Получаем информацию о курсе
                    course = self.db.get_course(module['course_id'])
                    if course:
                        # Удаляем модуль из GitHub
                        if module['github_path']:
                            repo = self.github_api.get_course(course['title'])
                            self.github_api.delete_module(repo, module['title'])
                        
                        # Удаляем модуль из Gushub
                        if module.get('site_id'):
                            self.gushub_api.delete_module(module['site_id'])
                
                # Удаляем модуль из базы данных
                self.db.delete_module(self.current_module_id)
                self.set_current_module(None)
                # Отправляем сигнал для обновления дерева
                self.tree_update_needed.emit()
                
                # Показываем сообщение об успешном удалении
                QMessageBox.information(
                    self,
                    "Успех",
                    f"Модуль '{module['title']}' успешно удален"
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось удалить модуль: {str(e)}"
                )
    
    def create_lesson(self):
        """Создание нового урока для текущего модуля"""
        if self.current_module_id is None:
            return
        
        dialog = CreateLessonDialog(self.current_module_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            title, file_path = dialog.get_lesson_data()
            if title and file_path:  # Проверяем, что название не пустое и файл выбран
                try:
                    # Получаем информацию о модуле и курсе
                    module = self.db.get_module(self.current_module_id)
                    course = self.db.get_course(module['course_id'])
                    
                    # Проверяем уникальность названия
                    lessons = self.db.get_lessons_by_module(self.current_module_id)
                    tasks = self.db.get_tasks_by_module(self.current_module_id)
                    
                    # Проверяем уроки
                    for lesson in lessons:
                        if lesson['title'].lower() == title.lower():
                            QMessageBox.warning(
                                self,
                                "Ошибка",
                                f"Урок с названием '{title}' уже существует в этом модуле"
                            )
                            return
                    
                    # Проверяем задачи
                    for task in tasks:
                        if task['title'].lower() == title.lower():
                            QMessageBox.warning(
                                self,
                                "Ошибка",
                                f"Задача с названием '{title}' уже существует в этом модуле"
                            )
                            return
                    
                    if course and course['github_path']:
                        # Получаем репозиторий курса
                        repo = self.github_api.get_course(course['title'])
                        # Создаем урок в репозитории
                        lesson_path = self.github_api.create_lesson(repo, module['title'], title, file_path)
                        # Получаем raw URL для файла и кодируем его
                        raw_url = f"https://raw.githubusercontent.com/{self.github_api.user.login}/{repo.name}/main/{lesson_path}"
                        encoded_url = urllib.parse.quote(raw_url, safe=':/?=&')
                        
                        # Создаем урок в Gushub
                        if module.get('site_id'):
                            # Преобразуем в словарь для отправки
                            lesson_dict = {
                                'title': title,
                                'urlMd': encoded_url
                            }
                            gushub_response = self.gushub_api.create_lesson(module['site_id'], lesson_dict)
                            
                            # Добавляем урок в базу данных
                            self.db.add_lesson(
                                self.current_module_id,
                                lesson_path,
                                title,
                                raw_url,  # Сохраняем оригинальный URL в базу
                                site_id=gushub_response['id']
                            )
                            
                            # Отправляем сигнал для обновления дерева
                            self.tree_update_needed.emit()
                            
                            # Показываем сообщение об успешном создании
                            QMessageBox.information(
                                self,
                                "Успех",
                                f"Урок '{title}' успешно создан в модуле '{module['title']}'"
                            )
                        else:
                            raise Exception("Не найден ID модуля в Gushub")
                    
                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Ошибка",
                        f"Не удалось создать урок: {str(e)}"
                    )
