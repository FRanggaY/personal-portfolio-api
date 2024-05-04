from sqlalchemy.orm import Session

from app.models.project.project_translation import ProjectTranslation
from app.repositories.project.project_translation_repository import ProjectTranslationRepository

class ProjectTranslationService:
    def __init__(self, db: Session):
        self.db = db
        self.project_translation_repository = ProjectTranslationRepository(db)

    def update_project_translation(
        self, 
        exist_project_translation: ProjectTranslation, 
        project_translation: ProjectTranslation,
    ):
        
        exist_project_translation.title = project_translation.title
        exist_project_translation.description = project_translation.description

        return self.project_translation_repository.update_project_translation(exist_project_translation)