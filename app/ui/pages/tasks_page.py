from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QMessageBox, QDialog, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from app.database.database import Database
from app.ui.forms.tasks_update_form import UpdateTaskDialog
from app.api.github_api import GitHubAPI
from app.api.gushub_api import GushubAPI
from app.settings import AppSettings

class TasksPage(QWidget):
    # Сигнал для обновления дерева
    tree_update_needed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.settings = AppSettings()
        self.github_api = GitHubAPI(self.settings.get_github_token())
        self.gushub_api = GushubAPI()
        self.current_task_id = None
        
        # Создаем основной layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(30)
        
        # Заголовок страницы
        title_label = QLabel("<h1>Управление задачами</h1>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        main_layout.addWidget(title_label)
        
        # Фрейм для информации о задаче
        task_frame = QFrame()
        task_layout = QVBoxLayout(task_frame)
        task_layout.setContentsMargins(20, 20, 20, 20)
        
        # Информация о задаче
        self.task_info = QLabel("<h2>Задача не выбрана</h2>")
        self.task_info.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.task_info.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        task_layout.addWidget(self.task_info)
        
        main_layout.addWidget(task_frame, 1)  # Растягиваем фрейм с информацией
        
        # Кнопки управления
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(20)

        self.update_task_button = QPushButton("Обновить контент")
        self.update_task_button.clicked.connect(self.update_task)
        self.update_task_button.setEnabled(False)
        
        self.delete_task_button = QPushButton("Удалить задачу")
        self.delete_task_button.clicked.connect(self.delete_task)
        self.delete_task_button.setEnabled(False)
        
        buttons_layout.addWidget(self.update_task_button)
        buttons_layout.addWidget(self.delete_task_button)
        
        main_layout.addLayout(buttons_layout)
    
    def set_current_task(self, task_id: int | None):
        """Устанавливает текущую задачу и обновляет интерфейс"""
        self.current_task_id = task_id
        
        if task_id is None:
            self.task_info.setText("<h2>Задача не выбрана</h2>")
            self.update_task_button.setEnabled(False)
            self.delete_task_button.setEnabled(False)
        else:
            task = self.db.get_task(task_id)
            if task:
                self.task_info.setText(
                    f"<h2><b>Название:</b> {task['title']}</h2>"
                )
                self.update_task_button.setEnabled(True)
                self.delete_task_button.setEnabled(True)
    
    def update_task(self):
        """Обновление контента задачи"""
        if not self.current_task_id:
            return
            
        # Получаем данные задачи
        task = self.db.get_task(self.current_task_id)
        if not task:
            return
            
        # Получаем данные урока
        lesson = self.db.get_lesson(task['lesson_id'])
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
        dialog = UpdateTaskDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            file_path = dialog.get_file_path()
            
            if not file_path:
                QMessageBox.warning(self, "Ошибка", "Выберите файл с задачей")
                return
            
            try:
                # Получаем репозиторий курса
                repo = self.github_api.get_course(course['title'])
                if not repo:
                    raise Exception("Не удалось получить репозиторий курса")
                
                # Получаем SHA хеш текущего файла
                contents = repo.get_contents(task['github_path'])
                
                # Читаем содержимое нового файла
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Обновляем задачу в GitHub
                self.github_api.update_task(
                    repo=repo,
                    path=task['github_path'],
                    new_content=content,
                    commit_message=f"Update task {task['title']}",
                    sha=contents.sha
                )
                
                QMessageBox.information(self, "Успех", "Контент задачи успешно обновлен")
                
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось обновить контент задачи: {str(e)}")
    
    def delete_task(self):
        """Удаление текущей задачи"""
        if self.current_task_id is None:
            return
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение удаления")
        msg_box.setText("Вы уверены, что хотите удалить эту задачу?")
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.No)
        
        # Устанавливаем русский текст для кнопок
        yes_button = msg_box.button(QMessageBox.StandardButton.Yes)
        yes_button.setText("Да")
        no_button = msg_box.button(QMessageBox.StandardButton.No)
        no_button.setText("Нет")
        
        if msg_box.exec() == QMessageBox.StandardButton.Yes:
            try:
                # Получаем информацию о задаче
                task = self.db.get_task(self.current_task_id)
                if task and task['github_path']:
                    # Получаем информацию об уроке, модуле и курсе
                    lesson = self.db.get_lesson(task['lesson_id'])
                    if lesson:
                        module = self.db.get_module(lesson['module_id'])
                        if module:
                            course = self.db.get_course(module['course_id'])
                            if course:
                                # Получаем репозиторий курса
                                repo = self.github_api.get_course(course['title'])
                                # Получаем SHA хеш файла
                                contents = repo.get_contents(task['github_path'])
                                # Удаляем задачу из репозитория
                                self.github_api.delete_task(repo, task['github_path'], contents.sha)

                                # Удаляем задачу из Gushub
                                if task.get('site_id'):
                                    self.gushub_api.delete_step(task['site_id'])
                
                # Удаляем задачу из базы данных
                self.db.delete_task(self.current_task_id)
                self.set_current_task(None)
                # Отправляем сигнал для обновления дерева
                self.tree_update_needed.emit()
                
                # Показываем сообщение об успешном удалении
                QMessageBox.information(
                    self,
                    "Успех",
                    f"Задача '{task['title']}' успешно удалена"
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Ошибка",
                    f"Не удалось удалить задачу: {str(e)}"
                )
