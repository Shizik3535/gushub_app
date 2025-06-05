import requests
from typing import Dict, Optional
from datetime import datetime


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

# API Client
class GushubAPI:
    BASE_URL = "https://gushub.ru"
    
    def __init__(self):
        self.session = requests.Session()
        self.user_id = None
        self.access_token = None
        self.refresh_token = None
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make authenticated request to the API"""
        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.request(method, url, json=data)
        response.raise_for_status()
        return response.json()
    
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
        return self._make_request('POST', '/api/upload', {'photo': (photo_path, open(photo_path, 'rb'), 'image/jpeg')})
    
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
