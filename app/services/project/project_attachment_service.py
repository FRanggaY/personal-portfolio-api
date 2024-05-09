import os
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.project.project import Project

from app.models.project.project_attachment import ProjectAttachment
from app.repositories.project.project_attachment_repository import ProjectAttachmentRepository
from app.utils.handling_file import delete_file, upload_file

class ProjectAttachmentService:
    def __init__(self, db: Session):
        self.db = db
        self.project_attachment_repository = ProjectAttachmentRepository(db)
        self.static_folder_image = "static/images/project/attachment"

    def create_project_attachment(self, project_attachment: ProjectAttachment, exist_project: Project, image: UploadFile = None, file_extension_image = None):
        project_attachment.image_url = upload_file(image, self.static_folder_image, file_extension_image,  f"{exist_project.user.username}-{exist_project.title}-{project_attachment.title}") if image else ''

        return self.project_attachment_repository.create_project_attachment(project_attachment)

    def update_project_attachment(
        self, 
        exist_project_attachment: ProjectAttachment, 
        project_attachment: ProjectAttachment,
        exist_project: Project,
        image: UploadFile = None,
        file_extension_image = None,
        ):
        if image and not exist_project_attachment.image_url:
            exist_project_attachment.image_url = upload_file(image, self.static_folder_image, file_extension_image,  f"{exist_project.user.username}-{exist_project.title}-{project_attachment.title}")

        if image and exist_project_attachment.image_url:
            file_path = os.path.join(self.static_folder_image, exist_project_attachment.image_url)
            delete_file(file_path)
            exist_project_attachment.image_url = upload_file(image, self.static_folder_image, file_extension_image,  f"{exist_project.user.username}-{exist_project.title}-{project_attachment.title}")
        
        exist_project_attachment.title = project_attachment.title
        exist_project_attachment.is_active = project_attachment.is_active
        exist_project_attachment.description = project_attachment.description
        exist_project_attachment.category = project_attachment.category
        exist_project_attachment.website_url = project_attachment.website_url

        return self.project_attachment_repository.update_project_attachment(exist_project_attachment)

    def delete_project_attachment(self, project_attachment_id: str):
        project_attachment = self.project_attachment_repository.read_project_attachment(project_attachment_id)
        if not project_attachment:
            raise ValueError("Project Attachment not found")

        if project_attachment.image_url:
            file_path = os.path.join(self.static_folder_image, project_attachment.image_url)
            delete_file(file_path)

        return self.project_attachment_repository.delete_project_attachment(project_attachment)
