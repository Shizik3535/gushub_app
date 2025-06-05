from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QMessageBox, QDialog, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from app.database.database import Database
from app.ui.forms.tasks_add_form import CreateTaskDialog
from app.ui.forms.lessons_update_form import UpdateLessonDialog
from app.api.github_api import GitHubAPI
from app.api.gushub_api import GushubAPI
from app.settings import AppSettings
import urllib.parse

class LessonsPage(QWidget):
    # Сигнал для обновления дерева
    tree_update_needed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.settings = AppSettings()
        self.github_api = GitHubAPI(self.settings.get_github_token())
        self.gushub_api = GushubAPI()
        self.current_lesson_id = None
        
        # Создаем основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(30)
        
        # Заголовок страницы
        title_label = QLabel("<h1>Управление уроками</h1>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_layout.addWidget(title_label)
        
        # Фрейм для информации об уроке
        lesson_frame = QFrame()
        lesson_layout = QVBoxLayout(lesson_frame)
        lesson_layout.setContentsMargins(20, 20, 20, 20)
        
        # Информация об уроке
        self.lesson_info = QLabel("<h2>Урок не выбран</h2>")
        self.lesson_info.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.lesson_info.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        lesson_layout.addWidget(self.lesson_info)
        
        main_layout.addWidget(lesson_frame, 1)  # Растягиваем фрейм с информацией
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        self.update_lesson_button = QPushButton("Обновить контент")
        self.update_lesson_button.clicked.connect(self.update_lesson)
        self.update_lesson_button.setEnabled(False)
        
        self.delete_lesson_button = QPushButton("Удалить урок")
        self.delete_lesson_button.clicked.connect(self.delete_lesson)
        self.delete_lesson_button.setEnabled(False)
        
        self.create_task_button = QPushButton("Создать задачу")
        self.create_task_button.clicked.connect(self.create_task)
        self.create_task_button.setEnabled(False)
        
        buttons_layout.addWidget(self.update_lesson_button)
        buttons_layout.addWidget(self.delete_lesson_button)
        buttons_layout.addWidget(self.create_task_button)
        
        main_layout.addLayout(buttons_layout)
    
    def set_current_lesson(self, lesson_id: int | None):
        """Устанавливает текущий урок и обновляет интерфейс"""
        self.current_lesson_id = lesson_id
        
        if lesson_id is None:
            self.lesson_info.setText("<h2>Урок не выбран</h2>")
            self.update_lesson_button.setEnabled(False)
            self.delete_lesson_button.setEnabled(False)
            self.create_task_button.setEnabled(False)
        else:
            lesson = self.db.get_lesson(lesson_id)
            if lesson:
                self.lesson_info.setText(
                    f"<h2><b>Название:</b> {lesson['title']}</h2>"
                )
                self.update_lesson_button.setEnabled(True)
                self.delete_lesson_button.setEnabled(True)
                self.create_task_button.setEnabled(True)
    
    def update_lesson(self):
        """Обновление контента урока"""
        if not self.current_lesson_id:
            return
            
        # Получаем данные урока
        lesson = self.db.get_lesson(self.current_lesson_id)
        if not lesson:
            return
            
        # Получаем данные модуля
        module = self.db.get_module(lesson['module_id'])
        if not module:
            return
            
        # Получаем данные курса
        course = self.db.get_course(module['course_id'])
        if not course:
            return
            
        # Создаем диалог
        dialog = UpdateLessonDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            file_path = dialog.get_file_path()
            
            if not file_path:
                QMessageBox.warning(self, "Ошибка", "Выберите файл с уроком")
                return
            
            try:
                # Получаем репозиторий курса
                repo = self.github_api.get_course(course['title'])
                if not repo:
                    raise Exception("Не удалось получить репозиторий курса")
                
                # Получаем SHA хеш текущего файла
                contents = repo.get_contents(lesson['github_path'])
                
                # Читаем содержимое нового файла
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Обновляем урок в GitHub
                self.github_api.update_lesson(
                    repo=repo,
                    path=lesson['github_path'],
                    new_content=content,
                    commit_message=f"Update lesson {lesson['title']}",
                    sha=contents.sha
                )
                
                QMessageBox.information(self, "Успех", "Контент урока успешно обновлен")
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить контент урока: {str(e)}")
    
    def delete_lesson(self):
        """Удаление текущего урока"""
        if self.current_lesson_id is None:
            return
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение удаления")
        msg_box.setText("Вы уверены, что хотите удалить этот урок?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        # Устанавливаем русский текст для кнопок
        yes_button = msg_box.button(QMessageBox.StandardButton.Yes)
        yes_button.setText("Да")
        no_button = msg_box.button(QMessageBox.StandardButton.No)
        no_button.setText("Нет")
        
        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            try:
                # Получаем информацию об уроке
                lesson = self.db.get_lesson(self.current_lesson_id)
                if lesson and lesson['github_path']:
                    # Получаем информацию о модуле и курсе
                    module = self.db.get_module(lesson['module_id'])
                    if module:
                        course = self.db.get_course(module['course_id'])
                        if course:
                            # Получаем репозиторий курса
                            repo = self.github_api.get_course(course['title'])
                            
                            # Получаем все задачи урока
                            tasks = self.db.get_tasks_by_lesson(self.current_lesson_id)
                            
                            # Удаляем все задачи урока из GitHub
                            for task in tasks:
                                if task['github_path']:
                                    contents = repo.get_contents(task['github_path'])
                                    self.github_api.delete_task(repo, task['github_path'], contents.sha)
                            
                            # Получаем SHA хеш файла урока
                            contents = repo.get_contents(lesson['github_path'])
                            # Удаляем урок из репозитория
                            self.github_api.delete_lesson(repo, lesson['github_path'], contents.sha)

                            # Удаляем урок из Gushub
                            if lesson.get('site_id'):
                                self.gushub_api.delete_lesson(lesson['site_id'])
                
                # Удаляем урок из базы данных (это также удалит все связанные задачи)
                self.db.delete_lesson(self.current_lesson_id)
                self.set_current_lesson(None)
                # Отправляем сигнал для обновления дерева
                self.tree_update_needed.emit()
                
                # Показываем сообщение об успешном удалении
                QMessageBox.information(
                    self,
                    "Успех",
                    f"Урок '{lesson['title']}' и все его задачи успешно удалены"
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось удалить урок: {str(e)}"
                )
    
    def create_task(self):
        """Создание новой задачи"""
        if not self.current_lesson_id:
            return
            
        # Получаем данные урока
        lesson = self.db.get_lesson(self.current_lesson_id)
        if not lesson:
            return
            
        # Получаем данные модуля
        module = self.db.get_module(lesson['module_id'])
        if not module:
            return
            
        # Получаем данные курса
        course = self.db.get_course(module['course_id'])
        if not course:
            return
            
        # Создаем диалог
        dialog = CreateTaskDialog(self.current_lesson_id, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            title, file_path = dialog.get_task_data()
            
            if not title or not file_path:
                QMessageBox.warning(self, "Ошибка", "Заполните все поля")
                return
            
            # Проверяем уникальность названия задачи
            # Получаем все задачи в текущем уроке
            tasks = self.db.get_tasks_by_lesson(self.current_lesson_id)
            if any(task['title'] == title for task in tasks):
                QMessageBox.warning(self, "Ошибка", "Задача с таким названием уже существует в этом уроке")
                return
                
            # Получаем все уроки в текущем модуле
            lessons = self.db.get_lessons_by_module(module['id'])
            if any(lesson['title'] == title for lesson in lessons):
                QMessageBox.warning(self, "Ошибка", "Название задачи не может совпадать с названием урока в этом модуле")
                return
            
            tasks = self.db.get_tasks_by_module(self.db.get_lesson(self.current_lesson_id)['module_id'])
            if any(task['title'] == title for task in tasks):
                QMessageBox.warning(self, "Ошибка", "Название задачи не может совпадать с названием задачи в этом модуле")
                return
            
            try:
                # Получаем репозиторий курса
                repo = self.github_api.get_course(course['title'])
                if not repo:
                    raise Exception("Не удалось получить репозиторий курса")
                
                # Читаем содержимое файла
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Создаем задачу в GitHub
                task_path = self.github_api.create_task(
                    repo=repo,
                    module_path=module['title'],
                    filename=title,
                    content=content,
                    commit_message=f"Add task {title}"
                )
                
                # Формируем raw URL для файла
                raw_url = f"https://raw.githubusercontent.com/{self.github_api.user.login}/{repo.name}/main/{task_path}"
                encoded_url = urllib.parse.quote(raw_url, safe=':/?=&')
                
                # Создаем задачу в Gushub
                if lesson.get('site_id'):
                    step_data = {
                        'title': title,
                        'urlMd': encoded_url,
                        'type': 'ASSIGNMENT'
                    }
                    gushub_response = self.gushub_api.create_step(lesson['site_id'], step_data)
                    
                    # Сохраняем задачу в базе данных
                    self.db.add_task(
                        self.current_lesson_id,
                        task_path,
                        title,
                        raw_url,
                        site_id=gushub_response['id']
                    )
                else:
                    # Сохраняем задачу в базе данных без site_id
                    self.db.add_task(
                        self.current_lesson_id,
                        task_path,
                        title,
                        raw_url
                    )
                
                # Обновляем дерево
                self.tree_update_needed.emit()
                
                QMessageBox.information(self, "Успех", "Задача успешно создана")
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось создать задачу: {str(e)}")
