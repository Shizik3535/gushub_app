from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QFrame,
                            QHBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem,
                            QStackedWidget, QHeaderView, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal
from app.api.gushub_api import GushubAPI

class StudentsListWidget(QWidget):
    """Виджет для отображения списка студентов"""
    student_selected = pyqtSignal(int)  # Сигнал с ID выбранного студента
    back_clicked = pyqtSignal()  # Сигнал для возврата к выбору раздела
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gushub_api = GushubAPI()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Добавляем поиск
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск студента...")
        self.search_input.textChanged.connect(self.filter_students)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Добавляем таблицу студентов
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Имя пользователя", "Полное имя"])
        self.table.verticalHeader().setVisible(False)  # Скрываем боковую нумерацию
        self.table.horizontalHeader().setStretchLastSection(True)  # Растягиваем последнюю колонку
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Растягиваем первую колонку
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Растягиваем вторую колонку
        self.table.cellClicked.connect(self.on_student_selected)
        layout.addWidget(self.table)
        
        # Добавляем кнопку возврата
        back_button = QPushButton("← Вернуться к выбору раздела")
        back_button.clicked.connect(self.back_clicked.emit)
        layout.addWidget(back_button)
    
    def load_data(self):
        """Загрузка данных о студентах"""
        try:
            users = self.gushub_api.get_users()
            self.table.setRowCount(len(users))
            for i, user in enumerate(users):
                self.table.setItem(i, 0, QTableWidgetItem(user.username))
                self.table.setItem(i, 1, QTableWidgetItem(f"{user.firstName} {user.lastName}".strip() or user.username))
        except Exception as e:
            print(f"Ошибка при загрузке данных о студентах: {str(e)}")
    
    def filter_students(self, text: str):
        """Фильтрация таблицы студентов"""
        for row in range(self.table.rowCount()):
            show_row = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    show_row = True
                    break
            self.table.setRowHidden(row, not show_row)
    
    def on_student_selected(self, row: int, column: int):
        """Обработка выбора студента"""
        try:
            users = self.gushub_api.get_users()
            student_id = users[row].id
            self.student_selected.emit(student_id)
        except Exception as e:
            print(f"Ошибка при выборе студента: {str(e)}")

class GroupsListWidget(QWidget):
    """Виджет для отображения списка групп"""
    group_selected = pyqtSignal(int)  # Сигнал с ID выбранной группы
    back_clicked = pyqtSignal()  # Сигнал для возврата к выбору раздела
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gushub_api = GushubAPI()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Добавляем поиск
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск группы...")
        self.search_input.textChanged.connect(self.filter_groups)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Добавляем таблицу групп
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Название", "Описание"])
        self.table.verticalHeader().setVisible(False)  # Скрываем боковую нумерацию
        self.table.horizontalHeader().setStretchLastSection(True)  # Растягиваем последнюю колонку
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Растягиваем первую колонку
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Растягиваем вторую колонку
        self.table.cellClicked.connect(self.on_group_selected)
        layout.addWidget(self.table)
        
        # Добавляем кнопку возврата
        back_button = QPushButton("← Вернуться к выбору раздела")
        back_button.clicked.connect(self.back_clicked.emit)
        layout.addWidget(back_button)
    
    def load_data(self):
        """Загрузка данных о группах"""
        try:
            groups = self.gushub_api.get_groups()
            self.table.setRowCount(len(groups))
            for i, group in enumerate(groups):
                self.table.setItem(i, 0, QTableWidgetItem(group.name))
                self.table.setItem(i, 1, QTableWidgetItem(group.description))
        except Exception as e:
            print(f"Ошибка при загрузке данных о группах: {str(e)}")
    
    def filter_groups(self, text: str):
        """Фильтрация таблицы групп"""
        for row in range(self.table.rowCount()):
            show_row = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    show_row = True
                    break
            self.table.setRowHidden(row, not show_row)
    
    def on_group_selected(self, row: int, column: int):
        """Обработка выбора группы"""
        try:
            groups = self.gushub_api.get_groups()
            group_id = groups[row].id
            self.group_selected.emit(group_id)
        except Exception as e:
            print(f"Ошибка при выборе группы: {str(e)}")

class StudentStatsWidget(QWidget):
    """Виджет для отображения статистики студента"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gushub_api = GushubAPI()
        self.setup_ui()

    def localize(self, value):
        return value if value not in (None, '', 'None') else 'Не задано'
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Добавляем заголовок и кнопку возврата
        header_layout = QHBoxLayout()
        self.title = QLabel("<h2>Статистика студента</h2>")
        self.back_button = QPushButton("← Назад к списку")
        header_layout.addWidget(self.title)
        header_layout.addWidget(self.back_button)
        layout.addLayout(header_layout)
        
        # Создаем сетку для карточек
        grid_layout = QGridLayout()
        grid_layout.setSpacing(5)
        
        # Карточка основной информации
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        info_frame.setMinimumHeight(200)
        info_layout = QVBoxLayout(info_frame)
        info_title = QLabel("<h3>Основная информация</h3>")
        info_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        info_layout.addWidget(info_title)
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        info_layout.addWidget(self.info_label)
        info_layout.addStretch(0)
        grid_layout.addWidget(info_frame, 0, 0)
        
        # Карточка курсов
        courses_frame = QFrame()
        courses_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        courses_frame.setMinimumHeight(200)
        courses_layout = QVBoxLayout(courses_frame)
        courses_title = QLabel("<h3>Статистика по курсам</h3>")
        courses_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        courses_layout.addWidget(courses_title)
        self.courses_label = QLabel()
        self.courses_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        courses_layout.addWidget(self.courses_label)
        courses_layout.addStretch(0)
        grid_layout.addWidget(courses_frame, 0, 1)
        
        # Карточка заданий
        tasks_frame = QFrame()
        tasks_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        tasks_frame.setMinimumHeight(200)
        tasks_layout = QVBoxLayout(tasks_frame)
        tasks_title = QLabel("<h3>Статистика по заданиям</h3>")
        tasks_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        tasks_layout.addWidget(tasks_title)
        self.tasks_label = QLabel()
        self.tasks_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        tasks_layout.addWidget(self.tasks_label)
        tasks_layout.addStretch(0)
        grid_layout.addWidget(tasks_frame, 1, 0)
        
        # Карточка оценок
        grades_frame = QFrame()
        grades_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        grades_frame.setMinimumHeight(200)
        grades_layout = QVBoxLayout(grades_frame)
        grades_title = QLabel("<h3>Статистика по оценкам</h3>")
        grades_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        grades_layout.addWidget(grades_title)
        self.grades_label = QLabel()
        self.grades_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        grades_layout.addWidget(self.grades_label)
        grades_layout.addStretch(0)
        grid_layout.addWidget(grades_frame, 1, 1)
        
        layout.addLayout(grid_layout)

        # Кнопка эксыпорта
        export_layout = QHBoxLayout()
        self.export_button = QPushButton("Экспортировать в Excel")
        export_layout.addWidget(self.export_button)
        layout.addLayout(export_layout)

    def load_data(self, student_id: int):
        try:
            user = self.gushub_api.get_user(student_id)
            stats = self.gushub_api.get_user_statistics(student_id)
            grades_stats = self.gushub_api.get_user_grades_statistics(student_id)
            self.title.setText(f"<h2>Статистика студента: {self.localize(user.username)}</h2>")

            # Основная информация
            info_text = f"""
            <table style='margin-top:0;'>
                <tr><td><b>Имя:</b></td><td>{self.localize(user.firstName)}</td></tr>
                <tr><td><b>Email:</b></td><td>{self.localize(user.email)}</td></tr>
                <tr><td><b>Роль:</b></td><td>{self.localize(user.role)}</td></tr>
                <tr><td><b>Дата регистрации:</b></td><td>{user.createdAt.strftime('%d.%m.%Y %H:%M') if user.createdAt else 'Не задано'}</td></tr>
            </table>
            """
            self.info_label.setText(info_text)

            # Курсы
            courses_text = f"""
            <table style='margin-top:0;'>
                <tr><td><b>Всего курсов:</b></td><td>{self.localize(stats.totalCourses)}</td></tr>
                <tr><td><b>Завершено курсов:</b></td><td>{self.localize(stats.completedCourses)}</td></tr>
                <tr><td><b>В процессе:</b></td><td>{self.localize(stats.totalCourses - stats.completedCourses if stats.totalCourses is not None and stats.completedCourses is not None else None)}</td></tr>
                <tr><td><b>Общее время обучения:</b></td><td>{self.localize(stats.totalTimeSpent)} минут</td></tr>
            </table>
            """
            self.courses_label.setText(courses_text)

            # Задания
            percent = (stats.completedTasks / stats.totalTasks * 100) if stats.totalTasks else 0
            tasks_text = f"""
            <table style='margin-top:0;'>
                <tr><td><b>Всего заданий:</b></td><td>{self.localize(stats.totalTasks)}</td></tr>
                <tr><td><b>Выполнено заданий:</b></td><td>{self.localize(stats.completedTasks)}</td></tr>
                <tr><td><b>В процессе:</b></td><td>{self.localize(stats.totalTasks - stats.completedTasks if stats.totalTasks is not None and stats.completedTasks is not None else None)}</td></tr>
                <tr><td><b>Процент выполнения:</b></td><td>{percent:.1f}%</td></tr>
            </table>
            """
            self.tasks_label.setText(tasks_text)

            # Оценки
            grades_text = f"""
            <table style='margin-top:0;'>
                <tr><td><b>Средний балл:</b></td><td>{self.localize(f'{grades_stats.averageGrade:.1f}' if grades_stats.averageGrade is not None else None)}</td></tr>
                <tr><td><b>Всего оценок:</b></td><td>{self.localize(grades_stats.totalGrades)}</td></tr>
                <tr><td colspan='2'><b>Распределение оценок:</b></td></tr>
                <tr><td>2:</td><td>{self.localize(grades_stats.gradesByValue.get('2'))}</td></tr>
                <tr><td>3:</td><td>{self.localize(grades_stats.gradesByValue.get('3'))}</td></tr>
                <tr><td>4:</td><td>{self.localize(grades_stats.gradesByValue.get('4'))}</td></tr>
                <tr><td>5:</td><td>{self.localize(grades_stats.gradesByValue.get('5'))}</td></tr>
            </table>
            """
            self.grades_label.setText(grades_text)

        except Exception as e:
            import traceback
            print(f"\nОшибка при загрузке статистики студента:")
            print(f"ID студента: {student_id}")
            print(f"Тип ошибки: {type(e).__name__}")
            print(f"Сообщение ошибки: {str(e)}")
            print("Трассировка стека:")
            print(traceback.format_exc())
            self.info_label.setText("Ошибка при загрузке данных")
            self.courses_label.setText("")
            self.tasks_label.setText("")
            self.grades_label.setText("")

class GroupStatsWidget(QWidget):
    """Виджет для отображения статистики группы"""
    student_selected = pyqtSignal(int)  # Сигнал с ID выбранного студента

    def __init__(self, parent=None):
        super().__init__(parent)
        self.gushub_api = GushubAPI()
        self.setup_ui()

    def localize(self, value):
        return value if value not in (None, '', 'None') else 'Не задано'
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Заголовок и кнопка возврата
        header_layout = QHBoxLayout()
        self.title = QLabel("<h2>Статистика группы</h2>")
        self.back_button = QPushButton("← Назад к списку")
        header_layout.addWidget(self.title)
        header_layout.addWidget(self.back_button)
        layout.addLayout(header_layout)

        # Сетка для карточек
        grid_layout = QGridLayout()
        grid_layout.setSpacing(5)

        # Карточка основной информации
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        info_frame.setMinimumHeight(200)
        info_layout = QVBoxLayout(info_frame)
        info_title = QLabel("<h3>Основная информация</h3>")
        info_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        info_layout.addWidget(info_title)
        self.info_label = QLabel()
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        info_layout.addWidget(self.info_label)
        info_layout.addStretch(0)
        grid_layout.addWidget(info_frame, 0, 0)

        # Карточка участников (таблица)
        members_frame = QFrame()
        members_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        members_frame.setMinimumHeight(200)
        members_layout = QVBoxLayout(members_frame)
        members_title = QLabel("<h3>Участники</h3>")
        members_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        members_layout.addWidget(members_title)
        self.members_table = QTableWidget()
        self.members_table.setColumnCount(2)
        self.members_table.setHorizontalHeaderLabels(["Имя", "Логин"])
        self.members_table.verticalHeader().setVisible(False)
        self.members_table.horizontalHeader().setStretchLastSection(True)
        self.members_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.members_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.members_table.cellClicked.connect(self.on_member_selected)
        members_layout.addWidget(self.members_table)
        members_layout.addStretch(0)
        grid_layout.addWidget(members_frame, 0, 1)

        # Карточка курсов
        courses_frame = QFrame()
        courses_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        courses_frame.setMinimumHeight(200)
        courses_layout = QVBoxLayout(courses_frame)
        courses_title = QLabel("<h3>Курсы группы</h3>")
        courses_title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        courses_layout.addWidget(courses_title)
        self.courses_label = QLabel()
        self.courses_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        courses_layout.addWidget(self.courses_label)
        courses_layout.addStretch(0)
        grid_layout.addWidget(courses_frame, 1, 0, 1, 2)

        layout.addLayout(grid_layout)

        # Кнопка экспорта
        export_layout = QHBoxLayout()
        self.export_button = QPushButton("Экспортировать в Excel")
        export_layout.addWidget(self.export_button)
        layout.addLayout(export_layout)

    def load_data(self, group_id: int):
        try:
            group = self.gushub_api.get_group(group_id)
            self.title.setText(f"<h2>Статистика группы: {self.localize(group.name)}</h2>")

            # Основная информация
            info_text = f"""
            <table style='margin-top:0;'>
                <tr><td><b>Название:</b></td><td>{self.localize(group.name)}</td></tr>
                <tr><td><b>Описание:</b></td><td>{self.localize(group.description)}</td></tr>
                <tr><td><b>Код приглашения:</b></td><td>{self.localize(group.inviteCode)}</td></tr>
                <tr><td><b>Дата создания:</b></td><td>{group.createdAt.strftime('%d.%m.%Y %H:%M') if group.createdAt else 'Не задано'}</td></tr>
                <tr><td><b>Дата обновления:</b></td><td>{group.updatedAt.strftime('%d.%m.%Y %H:%M') if group.updatedAt else 'Не задано'}</td></tr>
                <tr><td><b>Количество участников:</b></td><td>{len(group.members)}</td></tr>
                <tr><td><b>Количество курсов:</b></td><td>{len(group.courses)}</td></tr>
            </table>
            """
            self.info_label.setText(info_text)

            # Участники (таблица)
            self._member_ids = []
            if group.members:
                self.members_table.setRowCount(len(group.members))
                for i, m in enumerate(group.members):
                    user = m.user
                    full_name = f"{self.localize(user.firstName)}".strip()
                    self.members_table.setItem(i, 0, QTableWidgetItem(full_name))
                    self.members_table.setItem(i, 1, QTableWidgetItem(self.localize(user.username)))
                    self._member_ids.append(user.id)
                self.members_table.setEnabled(True)
                self.members_table.setStyleSheet("")
            else:
                self.members_table.setRowCount(0)
                self.members_table.setEnabled(False)
                self.members_table.setStyleSheet("QTableWidget { color: #888; font-style: italic; }")
                # Показываем надпись по центру таблицы
                self.members_table.setRowCount(1)
                self.members_table.setSpan(0, 0, 1, 2)
                item = QTableWidgetItem("Нет участников")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
                self.members_table.setItem(0, 0, item)
                self._member_ids = []

            # Курсы
            if group.courses:
                courses_text = "<table style='margin-top:0;'>"
                courses_text += "<tr><th>Название курса</th></tr>"
                for c in group.courses:
                    title = c['title'] if isinstance(c, dict) and 'title' in c else str(c)
                    courses_text += f"<tr><td>{self.localize(title)}</td></tr>"
                courses_text += "</table>"
                self.courses_label.setText(courses_text)
                self.courses_label.setAlignment(Qt.AlignmentFlag.AlignTop)
            else:
                self.courses_label.setText("Нет курсов")
                self.courses_label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

        except Exception as e:
            import traceback
            print(f"\nОшибка при загрузке статистики группы:")
            print(f"ID группы: {group_id}")
            print(f"Тип ошибки: {type(e).__name__}")
            print(f"Сообщение ошибки: {str(e)}")
            print("Трассировка стека:")
            print(traceback.format_exc())
            self.info_label.setText("Ошибка при загрузке данных")
            self.members_table.setRowCount(0)
            self.courses_label.setText("")

    def on_member_selected(self, row: int, column: int):
        # Если нет участников, не реагируем
        if not self.members_table.isEnabled():
            return
        try:
            user_id_item = self.members_table.item(row, 1)
            # Получаем ID студента из исходных данных (лучше хранить список id)
            # Для этого сохраним список id в self._member_ids при загрузке
            student_id = self._member_ids[row]
            self.student_selected.emit(student_id)
        except Exception as e:
            print(f"Ошибка при выборе студента из группы: {str(e)}")

class SelectionWidget(QWidget):
    """Виджет для выбора раздела аналитики"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Создаем горизонтальный layout для кнопок
        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Добавляем кнопки выбора раздела
        students_button = QPushButton("Список студентов")
        groups_button = QPushButton("Список групп")
        students_button.setFixedWidth(250)
        groups_button.setFixedWidth(250)
        
        # Добавляем кнопки в горизонтальный layout
        buttons_layout.addWidget(students_button)
        buttons_layout.addWidget(groups_button)
        
        # Добавляем горизонтальный layout в основной layout
        layout.addLayout(buttons_layout)
        
        # Подключаем сигналы
        self.students_clicked = students_button.clicked
        self.groups_clicked = groups_button.clicked

class AnalyticsPage(QWidget):
    show_courses_page = pyqtSignal()  # Сигнал для возврата к курсам
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        # Создаем основной layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(30)
        
        # Добавляем заголовок
        title_label = QLabel("<h1>Аналитика</h1>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(title_label)
        
        # Создаем основной контент
        content_frame = QFrame()
        content_frame.setFrameStyle(QFrame.Shape.StyledPanel | QFrame.Shadow.Raised)
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        
        # Создаем стек виджетов для переключения между разделами
        self.stacked_widget = QStackedWidget()
        
        # Создаем виджеты для списков и статистики
        self.selection = SelectionWidget()
        self.students_list = StudentsListWidget()
        self.groups_list = GroupsListWidget()
        self.student_stats = StudentStatsWidget()
        self.group_stats = GroupStatsWidget()
        
        # Подключаем сигналы
        self.selection.students_clicked.connect(self.show_students_list)
        self.selection.groups_clicked.connect(self.show_groups_list)
        self.students_list.student_selected.connect(self.show_student_stats)
        self.groups_list.group_selected.connect(self.show_group_stats)
        self.students_list.back_clicked.connect(self.show_selection)
        self.groups_list.back_clicked.connect(self.show_selection)
        self.student_stats.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.group_stats.back_button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        self.group_stats.student_selected.connect(self.show_student_stats)
        
        # Добавляем виджеты в стек
        self.stacked_widget.addWidget(self.selection)
        self.stacked_widget.addWidget(self.students_list)
        self.stacked_widget.addWidget(self.groups_list)
        self.stacked_widget.addWidget(self.student_stats)
        self.stacked_widget.addWidget(self.group_stats)
        
        # Добавляем фрейм в основной layout
        layout.addWidget(self.stacked_widget)
        
        # Добавляем кнопку возврата
        return_button = QPushButton("Вернуться к курсам")
        return_button.clicked.connect(self.show_courses_page.emit)
        layout.addWidget(return_button)
    
    def show_selection(self):
        """Показать страницу выбора раздела"""
        self.stacked_widget.setCurrentIndex(0)
    
    def show_students_list(self):
        """Показать список студентов"""
        self.students_list.load_data()
        self.stacked_widget.setCurrentIndex(1)
    
    def show_groups_list(self):
        """Показать список групп"""
        self.groups_list.load_data()
        self.stacked_widget.setCurrentIndex(2)
    
    def show_student_stats(self, student_id: int):
        """Показать статистику студента"""
        self.student_stats.load_data(student_id)
        self.stacked_widget.setCurrentIndex(3)
    
    def show_group_stats(self, group_id: int):
        """Показать статистику группы"""
        self.group_stats.load_data(group_id)
        self.stacked_widget.setCurrentIndex(4)
