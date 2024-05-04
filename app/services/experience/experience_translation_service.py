from sqlalchemy.orm import Session

from app.models.experience.experience_translation import ExperienceTranslation
from app.repositories.experience.experience_translation_repository import ExperienceTranslationRepository

class ExperienceTranslationService:
    def __init__(self, db: Session):
        self.db = db
        self.experience_translation_repository = ExperienceTranslationRepository(db)

    def update_experience_translation(
        self, 
        exist_experience_translation: ExperienceTranslation, 
        experience_translation: ExperienceTranslation,
    ):
        
        exist_experience_translation.title = experience_translation.title
        exist_experience_translation.employee_type = experience_translation.employee_type
        exist_experience_translation.location = experience_translation.location
        exist_experience_translation.location_type = experience_translation.location_type
        exist_experience_translation.description = experience_translation.description

        return self.experience_translation_repository.update_experience_translation(exist_experience_translation)