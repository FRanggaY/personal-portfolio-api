import uuid
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from app.models.project.project_translation import ProjectTranslation

class ProjectTranslationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_project_translation(self, project: ProjectTranslation):
        project.id = str(uuid.uuid4())
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_project_translation_by_project_id_and_language_id(self, project_id: str, language_id: str) -> ProjectTranslation:
        return self.db.query(ProjectTranslation).filter(ProjectTranslation.project_id == project_id, ProjectTranslation.language_id == language_id).first()

    def update_project_translation(self, project: ProjectTranslation):
        self.db.commit()
        return project

    def delete_project_translation(self, project_translation: ProjectTranslation) -> str:
        project_translation_id = project_translation.id
        self.db.delete(project_translation)
        self.db.commit()
        return project_translation_id
