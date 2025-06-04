from github import Github, GithubException, Repository
import re
from transliterate import translit


class GitHubAPI:
    def __init__(self, token: str):
        self.github = Github(token)
        try:
            self.user = self.github.get_user()
        except GithubException as e:
            raise ValueError("Ошибка авторизации в GitHub API: " + str(e))

    def _make_valid_repo_name(self, name: str) -> str:
        name = translit(name, 'ru', reversed=True)
        name = name.lower().replace(" ", "-")
        name = re.sub(r"[^a-zA-Z0-9-_]", "", name)
        return name[:100]
    
    # Курсы
    def create_course(self, course_title: str, course_description: str) -> Repository.Repository:
        repo_name = self._make_valid_repo_name(course_title)
        try:
            repo = self.user.create_repo(
                name=repo_name,
                description=course_description,
                private=False
            )
            readme_content = f"# {course_title}\n\n{course_description}"
            repo.create_file("README.md", "Initial commit: course README", readme_content, branch="main")
            return repo
        except GithubException as e:
            raise RuntimeError("Ошибка при создании курса: " + str(e))
    
    def get_course(self, course_title: str) -> Repository.Repository:
        repo_name = self._make_valid_repo_name(course_title)
        try:
            repo = self.user.get_repo(repo_name)
            return repo
        except GithubException as e:
            raise RuntimeError("Ошибка при получении курса: " + str(e))
        
    def delete_course(self, repo_name: str):
        try:
            repo = self.user.get_repo(repo_name)
            repo.delete()
        except GithubException as e:
            raise RuntimeError("Ошибка при удалении курса: " + str(e))
        
    # Модули
    def create_module(self, repo: Repository.Repository, module_name: str, module_description: str) -> str:
        try:
            path = f"{module_name}/README.md"
            content = f"# {module_name}\n\n{module_description}"
            repo.create_file(path, f"Create module {module_name}", content, branch="main")
            return module_name
        except GithubException as e:
            raise RuntimeError("Ошибка при создании модуля: " + str(e))
        
    # Уроки
    def create_lesson(self, repo: Repository.Repository, module_path: str, filename: str, content: str,
                      commit_message: str) -> str:
        try:
            path = f"{module_path}/{filename}.md"
            repo.create_file(path, commit_message, content, branch="main")
            return path
        except GithubException as e:
            raise RuntimeError("Ошибка при создании урока: " + str(e))
        
    def update_lesson(self, repo: Repository.Repository, path: str, new_content: str, commit_message: str):
        try:
            repo.update_file(path, commit_message, new_content, branch="main")
        except GithubException as e:
            raise RuntimeError("Ошибка при обновлении урока: " + str(e))
        
    def delete_lesson(self, repo: Repository.Repository, path: str, message: str = "Delete file or folder"):
        try:
            repo.delete_file(path, message, branch="main")
        except GithubException as e:
            raise RuntimeError("Ошибка при удалении урока: " + str(e))
        
    # Задания
    def create_task(self, repo: Repository.Repository, module_path: str, filename: str, content: str,
                    commit_message: str) -> str:
        try:
            path = f"{module_path}/{filename}.md"
            repo.create_file(path, commit_message, content, branch="main")
            return path
        except GithubException as e:
            raise RuntimeError("Ошибка при создании задания: " + str(e))
        
    def update_task(self, repo: Repository.Repository, path: str, new_content: str, commit_message: str):
        try:
            repo.update_file(path, commit_message, new_content, branch="main")
        except GithubException as e:
            raise RuntimeError("Ошибка при обновлении задания: " + str(e))
        
    def delete_task(self, repo: Repository.Repository, path: str, message: str = "Delete file or folder"):
        try:
            repo.delete_file(path, message, branch="main")
        except GithubException as e:
            raise RuntimeError("Ошибка при удалении задания: " + str(e))
