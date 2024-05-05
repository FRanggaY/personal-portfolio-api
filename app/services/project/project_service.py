import os
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.models.project.project import Project
from app.repositories.project.project_repository import ProjectRepository
from app.utils.handling_file import delete_file, upload_file

class ProjectService:
    def __init__(self, db: Session):
        self.db = db
        self.project_repository = ProjectRepository(db)
        self.static_folder_image = "static/images/project/image"
        self.static_folder_logo = "static/images/project/logo"

    def create_project(self, project: Project, image: UploadFile = None, logo: UploadFile = None, file_extension_image = None, file_extension_logo = None):
        project.image_url = upload_file(image, self.static_folder_image, file_extension_image,  f"{project.user.username}-{project.title}") if image else ''
        project.logo_url = upload_file(logo, self.static_folder_logo, file_extension_logo, f"{project.user.username}-{project.title}") if logo else ''

        return self.project_repository.create_project(project)

    def update_project(
        self, 
        exist_project: Project, 
        project: Project,
        image: UploadFile = None,
        logo: UploadFile = None,
        file_extension_image = None,
        file_extension_logo = None,
    ):
        if image and not exist_project.image_url:
            exist_project.image_url = upload_file(image, self.static_folder_image, file_extension_image,  f"{project.user.username}-{project.title}")

        if image and exist_project.image_url:
            file_path = os.path.join(self.static_folder_image, exist_project.image_url)
            delete_file(file_path)
            exist_project.image_url = upload_file(image, self.static_folder_image, file_extension_image,  f"{project.user.username}-{project.title}")
        
        if logo and not exist_project.logo_url:
            exist_project.logo_url = upload_file(logo, self.static_folder_logo, file_extension_logo,  f"{project.user.username}-{project.title}")

        if logo and exist_project.logo_url:
            file_path = os.path.join(self.static_folder_logo, exist_project.logo_url)
            delete_file(file_path)
            exist_project.logo_url = upload_file(logo, self.static_folder_logo, file_extension_logo,  f"{project.user.username}-{project.title}")
        
        exist_project.title = project.title
        exist_project.is_active = project.is_active

        return self.project_repository.update_project(exist_project)

    def delete_project(self, project_id: str):
        project = self.project_repository.read_project(project_id)
        if not project:
            raise ValueError("Project not found")

        if project.image_url:
            file_path = os.path.join(self.static_folder_image, project.image_url)
            delete_file(file_path)
        
        if project.logo_url:
            file_path = os.path.join(self.static_folder_logo, project.logo_url)
            delete_file(file_path)

        return self.project_repository.delete_project(project)