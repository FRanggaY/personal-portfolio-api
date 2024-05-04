from sqlalchemy.orm import Session

from app.models.education.education_translation import EducationTranslation
from app.repositories.education.education_translation_repository import EducationTranslationRepository

class EducationTranslationService:
    def __init__(self, db: Session):
        self.db = db
        self.education_translation_repository = EducationTranslationRepository(db)

    def update_education_translation(
        self, 
        exist_education_translation: EducationTranslation, 
        education_translation: EducationTranslation,
    ):
        
        exist_education_translation.title = education_translation.title
        exist_education_translation.degree = education_translation.degree
        exist_education_translation.field_of_study = education_translation.field_of_study
        exist_education_translation.description = education_translation.description

        return self.education_translation_repository.update_education_translation(exist_education_translation)
