from github import Github, GithubException, Repository
import re
from transliterate import translit


class GitHubCourseManager:
    def __init__(self, github_token: str):
        self.github = Github(github_token)
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

    def delete_course(self, repo_name: str):
        try:
            repo = self.github.get_repo(f"{self.user.login}/{repo_name}")
            repo.delete()
        except GithubException as e:
            raise RuntimeError("Ошибка при удалении репозитория: " + str(e))

    # Модули
    def create_module(self, repo: Repository.Repository, folder_name: str, description: str) -> str:
        try:
            path = f"{folder_name}/README.md"
            content = f"# {folder_name}\n\n{description}"
            repo.create_file(path, f"Create module {folder_name}", content, branch="main")
            return folder_name
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
            file = repo.get_contents(path, ref="main")
            repo.update_file(file.path, commit_message, new_content, file.sha, branch="main")
        except GithubException as e:
            raise RuntimeError("Ошибка при обновлении урока: " + str(e))

    # Задачи
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
            file = repo.get_contents(path, ref="main")
            repo.update_file(file.path, commit_message, new_content, file.sha, branch="main")
        except GithubException as e:
            raise RuntimeError("Ошибка при обновлении задания: " + str(e))

    # Удаление модулей, уроков, задач
    def delete_file_or_folder(self, repo: Repository.Repository, path: str, message: str = "Delete file or folder"):
        try:
            contents = repo.get_contents(path, ref="main")
            if isinstance(contents, list):
                for content_file in contents:
                    repo.delete_file(content_file.path, message, content_file.sha, branch="main")
                repo.delete_file(path + "/README.md", message, repo.get_contents(path + "/README.md").sha,
                                 branch="main")
            else:
                repo.delete_file(contents.path, message, contents.sha, branch="main")
        except GithubException as e:
            raise RuntimeError("Ошибка при удалении: " + str(e))
