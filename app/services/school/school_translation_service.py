from sqlalchemy.orm import Session

from app.models.school.school_translation import SchoolTranslation
from app.repositories.school.school_translation_repository import SchoolTranslationRepository

class SchoolTranslationService:
    def __init__(self, db: Session):
        self.db = db
        self.school_translation_repository = SchoolTranslationRepository(db)

    def update_school_translation(
        self, 
        exist_school_translation: SchoolTranslation, 
        school_translation: SchoolTranslation,
    ):
        
        exist_school_translation.name = school_translation.name
        exist_school_translation.description = school_translation.description
        exist_school_translation.address = school_translation.address

        return self.school_translation_repository.update_school_translation(exist_school_translation)
    
    def delete_school_translation(self, school_id: str, language_id: str):
        school_translation = self.school_translation_repository.get_school_translation_by_school_id_and_language_id(school_id, language_id)
        if not school_translation:
            raise ValueError("School Translation not found")

        return self.school_translation_repository.delete_school_translation(school_translation)
