import requests
from typing import Dict, Optional, List
from datetime import datetime
from app.settings import AppSettings
import os


# -- Courses --
class CourseData:
    def __init__(self, title: str, description: str, image: str):
        self.title = title
        self.description = description
        self.image = image
    
class CourseResponse:
    def __init__(self, id: int, title: str, description: str, image: str, createdAt: datetime, updatedAt: datetime, modules: list):
        self.id = id
        self.title = title
        self.description = description
        self.image = image
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.modules = modules

# -- Modules -- 
class ModuleData:
    def __init__(self, title: str, description: str):
        self.title = title
        self.description = description

class ModuleResponse:
    def __init__(self, id: int, title: str, description: str, order: int, courseId: int, createdAt: datetime, updatedAt: datetime, lessons: list):
        self.id = id
        self.title = title
        self.description = description
        self.order = order
        self.courseId = courseId
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.lessons = lessons

# -- Lessons --
class LessonData:
    def __init__(self, title: str, urlMD: str):
        self.title = title
        self.urlMD = urlMD

class LessonResponse:
    def __init__(self, id: int, title: str, moduleId: int, urlMD: str, order: int, createdAt: datetime, updatedAt: datetime, steps: list):
        self.id = id
        self.title = title
        self.moduleId = moduleId
        self.urlMD = urlMD
        self.order = order
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.steps = steps

# -- Steps --
class StepData:
    def __init__(self, title: str, urlMD: str, type: str = "ASSIGNMENT"):
        self.title = title
        self.type = type
        self.urlMD = urlMD

class StepResponse:
    def __init__(self, id: int, title: str, type: str, urlMD: str, createdAt: datetime, updatedAt: datetime, lessonId: int, order: int):
        self.id = id
        self.title = title
        self.type = type
        self.urlMD = urlMD
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.lessonId = lessonId
        self.order = order

# -- Statistics --
# -- Groups --
class GroupData:
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description

class GroupCount:
    def __init__(self, members: int, courses: int):
        self.members = members
        self.courses = courses

class GroupResponse:
    def __init__(self, id: int, name: str, description: str, inviteCode: str, 
                 createdAt: datetime, updatedAt: datetime, _count: GroupCount):
        self.id = id
        self.name = name
        self.description = description
        self.inviteCode = inviteCode
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self._count = _count

# -- Users --
class UserData:
    def __init__(self, username: str, firstName: str = "", lastName: str = "", middleName: str = ""):
        self.username = username
        self.firstName = firstName
        self.lastName = lastName
        self.middleName = middleName

class UserResponse:
    def __init__(self, id: int, username: str, firstName: str, lastName: str, middleName: str,
                 avatar: str | None, isAdmin: bool, isBlocked: bool, blockReason: str | None,
                 createdAt: datetime, updatedAt: datetime, provider: str | None = None):
        self.id = id
        self.username = username
        self.firstName = firstName
        self.lastName = lastName
        self.middleName = middleName
        self.avatar = avatar
        self.isAdmin = isAdmin
        self.isBlocked = isBlocked
        self.blockReason = blockReason
        self.createdAt = createdAt
        self.updatedAt = updatedAt
        self.provider = provider

# -- Statistics --
class CourseProgress:
    def __init__(self, courseId: int, courseTitle: str, totalTasks: int, 
                 completedTasks: int, progressPercentage: int):
        self.courseId = courseId
        self.courseTitle = courseTitle
        self.totalTasks = totalTasks
        self.completedTasks = completedTasks
        self.progressPercentage = progressPercentage

class UserStatistics:
    def __init__(self, courseProgress: List[CourseProgress], totalCourses: int,
                 completedCourses: int, totalTasks: int, completedTasks: int,
                 totalTimeSpent: int):
        self.courseProgress = courseProgress
        self.totalCourses = totalCourses
        self.completedCourses = completedCourses
        self.totalTasks = totalTasks
        self.completedTasks = completedTasks
        self.totalTimeSpent = totalTimeSpent

# -- Grade Statistics --
class GradeLesson:
    def __init__(self, id: int, title: str, moduleTitle: str, courseTitle: str):
        self.id = id
        self.title = title
        self.moduleTitle = moduleTitle
        self.courseTitle = courseTitle

class GradeUser:
    def __init__(self, id: int, username: str, fullName: str):
        self.id = id
        self.username = username
        self.fullName = fullName

class RecentGrade:
    def __init__(self, id: int, value: int, feedback: str, createdAt: datetime,
                 lesson: GradeLesson, user: GradeUser):
        self.id = id
        self.value = value
        self.feedback = feedback
        self.createdAt = createdAt
        self.lesson = lesson
        self.user = user

class BestGradedLesson:
    def __init__(self, lessonId: int, lessonTitle: str, courseId: int, courseTitle: str,
                 moduleName: str, grade: int, gradedAt: datetime):
        self.lessonId = lessonId
        self.lessonTitle = lessonTitle
        self.courseId = courseId
        self.courseTitle = courseTitle
        self.moduleName = moduleName
        self.grade = grade
        self.gradedAt = gradedAt

class UserGradesStatistics:
    def __init__(self, totalGrades: int, gradesByValue: Dict[str, int],
                 bestGradedLesson: Optional[BestGradedLesson], averageGrade: float,
                 recentGrades: List[RecentGrade]):
        self.totalGrades = totalGrades
        self.gradesByValue = gradesByValue
        self.bestGradedLesson = bestGradedLesson
        self.averageGrade = averageGrade
        self.recentGrades = recentGrades

# API Client
class GushubAPI:
    BASE_URL = "https://gushub.ru"
    
    def __init__(self):
        self.session = requests.Session()
        self.user_id = None
        self.access_token = None
        self.refresh_token = None
        
        # Автоматическая авторизация при создании объекта
        settings = AppSettings()
        username = settings.get_gushub_login()
        password = settings.get_gushub_password()
        
        if username and password:
            try:
                self.login(username, password)
            except Exception as e:
                print(f"Ошибка авторизации в Gushub: {str(e)}")
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to the API"""
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = self.session.request(method, url, json=data)
            
            # Если получили 401, пробуем переавторизоваться
            if response.status_code == 401:
                settings = AppSettings()
                username = settings.get_gushub_login()
                password = settings.get_gushub_password()
                
                if username and password:
                    # Пробуем переавторизоваться
                    self.login(username, password)
                    # Повторяем запрос с новыми куками
                    response = self.session.request(method, url, json=data)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при выполнении запроса к {url}: {str(e)}")
            raise
    
    def login(self, username: str, password: str) -> Dict:
        """Login and store authentication data"""
        response = self._make_request('POST', '/api/auth/login', {'username': username, 'password': password})
        
        # Store authentication data
        self.user_id = response['user']['id']
        self.access_token = response['accessToken']
        self.refresh_token = response['refreshToken']
        
        # Set cookies
        self.session.cookies.set('user_id', str(self.user_id), domain='gushub.ru', path='/')
        self.session.cookies.set('access_token', self.access_token, domain='gushub.ru', path='/')
        self.session.cookies.set('refresh_token', self.refresh_token, domain='gushub.ru', path='/')
        
        return response
    
    def logout(self) -> Dict:
        """Logout and clear authentication data"""
        response = self._make_request('POST', '/api/auth/logout')
        
        # Clear authentication data
        self.user_id = None
        self.access_token = None
        self.refresh_token = None
        
        # Clear cookies
        self.session.cookies.clear()
        
        return response
    
    # Upload photo
    def upload_photo(self, photo_path: str) -> Dict:
        """Upload photo"""
        url = f"{self.BASE_URL}/api/uploads"
        with open(photo_path, 'rb') as photo_file:
            files = {
                'file': (
                    os.path.basename(photo_path),
                    photo_file,
                    'image/jpeg'
                )
            }
            headers = {
                'Accept': 'application/json'
            }
            response = self.session.post(url, files=files, headers=headers)
            response.raise_for_status()
            return response.json()
    
    # -- Courses --
    def create_course(self, course_data: Dict) -> Dict:
        """Create course"""
        return self._make_request('POST', '/api/courses', course_data)
    
    def delete_course(self, course_id: int) -> Dict:
        """Delete course"""
        return self._make_request('DELETE', f'/api/courses/{course_id}')
    
    def get_courses(self) -> Dict:
        """Get all courses"""
        return self._make_request('GET', '/api/courses')
    
    # -- Modules --
    def create_module(self, course_id: int, module_data: Dict) -> Dict:
        """Create module"""
        return self._make_request('POST', f'/api/courses/{course_id}/modules', module_data)
    
    def delete_module(self, module_id: int) -> Dict:
        """Delete module"""
        return self._make_request('DELETE', f'/api/courses/modules/{module_id}')
    
    # -- Lessons --
    def create_lesson(self, module_id: int, lesson_data: Dict) -> Dict:
        """Create lesson"""
        return self._make_request('POST', f'/api/courses/modules/{module_id}/lessons', lesson_data)
    
    def delete_lesson(self, lesson_id: int) -> Dict:
        """Delete lesson"""
        return self._make_request('DELETE', f'/api/courses/lessons/{lesson_id}')
    
    # -- Steps --
    def create_step(self, lesson_id: int, step_data: Dict) -> Dict:
        """Create step"""
        return self._make_request('POST', f'/api/courses/lessons/{lesson_id}/steps', step_data)
    
    def delete_step(self, step_id: int) -> Dict:
        """Delete step"""
        return self._make_request('DELETE', f'/api/courses/steps/{step_id}')
    
    # -- Statistics --
    # -- Users --
    def get_users(self) -> List[UserResponse]:
        """Get all users"""
        response = self._make_request('GET', '/api/users')
        return [
            UserResponse(
                id=user['id'],
                username=user['username'],
                firstName=user['firstName'],
                lastName=user['lastName'],
                middleName=user['middleName'],
                avatar=user['avatar'],
                isAdmin=user['isAdmin'],
                isBlocked=user['isBlocked'],
                blockReason=user['blockReason'],
                createdAt=datetime.fromisoformat(user['createdAt'].replace('Z', '+00:00')),
                updatedAt=datetime.fromisoformat(user['updatedAt'].replace('Z', '+00:00')),
                provider=user['provider']
            )
            for user in response
        ]
    
    def get_user(self, user_id: int) -> UserResponse:
        """Get user by id"""
        response = self._make_request('GET', f'/api/users/{user_id}')
        return UserResponse(
            id=response['id'],
            username=response['username'],
            firstName=response['firstName'],
            lastName=response['lastName'],
            middleName=response['middleName'],
            avatar=response['avatar'],
            isAdmin=response['isAdmin'],
            isBlocked=response['isBlocked'],
            blockReason=response['blockReason'],
            createdAt=datetime.fromisoformat(response['createdAt'].replace('Z', '+00:00')),
            updatedAt=datetime.fromisoformat(response['updatedAt'].replace('Z', '+00:00')),
            provider=response.get('provider')  # provider может отсутствовать в ответе
        )
    
    def get_user_statistics(self, user_id: int) -> UserStatistics:
        """Get user statistics"""
        response = self._make_request('GET', f'/api/users/{user_id}/statistics')
        
        # Преобразуем прогресс по курсам
        course_progress = [
            CourseProgress(
                courseId=progress['courseId'],
                courseTitle=progress['courseTitle'],
                totalTasks=progress['totalTasks'],
                completedTasks=progress['completedTasks'],
                progressPercentage=progress['progressPercentage']
            )
            for progress in response.get('courseProgress', [])
        ]
        
        # Создаем объект статистики
        return UserStatistics(
            courseProgress=course_progress,
            totalCourses=response.get('totalCourses', 0),
            completedCourses=response.get('completedCourses', 0),
            totalTasks=response.get('totalTasks', 0),
            completedTasks=response.get('completedTasks', 0),
            totalTimeSpent=response.get('totalTimeSpent', 0)
        )

    def get_user_grades_statistics(self, user_id: int) -> UserGradesStatistics:
        """Get user grades statistics"""
        response = self._make_request('GET', f'/api/users/{user_id}/grades/statistics')
        
        # Преобразуем лучший урок, если он есть
        best_lesson = None
        if response.get('bestGradedLesson'):
            best_lesson = BestGradedLesson(
                lessonId=response['bestGradedLesson']['lessonId'],
                lessonTitle=response['bestGradedLesson']['lessonTitle'],
                courseId=response['bestGradedLesson']['courseId'],
                courseTitle=response['bestGradedLesson']['courseTitle'],
                moduleName=response['bestGradedLesson']['moduleName'],
                grade=response['bestGradedLesson']['grade'],
                gradedAt=datetime.fromisoformat(response['bestGradedLesson']['gradedAt'].replace('Z', '+00:00'))
            )
        
        # Преобразуем последние оценки
        recent_grades = []
        for grade in response.get('recentGrades', []):
            lesson = GradeLesson(
                id=grade['lesson']['id'],
                title=grade['lesson']['title'],
                moduleTitle=grade['lesson']['moduleTitle'],
                courseTitle=grade['lesson']['courseTitle']
            )
            
            user = GradeUser(
                id=grade['user']['id'],
                username=grade['user']['username'],
                fullName=grade['user']['fullName']
            )
            
            recent_grades.append(RecentGrade(
                id=grade['id'],
                value=grade['value'],
                feedback=grade['feedback'],
                createdAt=datetime.fromisoformat(grade['createdAt'].replace('Z', '+00:00')),
                lesson=lesson,
                user=user
            ))
        
        # Создаем объект статистики
        return UserGradesStatistics(
            totalGrades=response.get('totalGrades', 0),
            gradesByValue=response.get('gradesByValue', {"2": 0, "3": 0, "4": 0, "5": 0}),
            bestGradedLesson=best_lesson,
            averageGrade=response.get('averageGrade', 0.0),
            recentGrades=recent_grades
        )
    
    # -- Groups --
    def get_groups(self) -> List[GroupResponse]:
        """Get all groups"""
        response = self._make_request('GET', '/api/groups')
        return [
            GroupResponse(
                id=group['id'],
                name=group['name'],
                description=group['description'],
                inviteCode=group['inviteCode'],
                createdAt=datetime.fromisoformat(group['createdAt'].replace('Z', '+00:00')),
                updatedAt=datetime.fromisoformat(group['updatedAt'].replace('Z', '+00:00')),
                _count=GroupCount(
                    members=group['_count']['members'],
                    courses=group['_count']['courses']
                )
            )
            for group in response
        ]
