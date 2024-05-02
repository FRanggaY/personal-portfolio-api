import uuid
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from app.models.education.education_translation import EducationTranslation

class EducationTranslationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_education_translation(self, education: EducationTranslation):
        education.id = str(uuid.uuid4())
        self.db.add(education)
        self.db.commit()
        self.db.refresh(education)
        return education

    def get_education_translation_by_education_id_and_language_id(self, education_id: str, language_id: str) -> EducationTranslation:
        return self.db.query(EducationTranslation).filter(EducationTranslation.education_id == education_id, EducationTranslation.language_id == language_id).first()

    def update_education_translation(self, education: EducationTranslation):
        self.db.commit()
        return education

    def delete_education_translation(self, education_translation: EducationTranslation) -> str:
        education_translation_id = education_translation.id
        self.db.delete(education_translation)
        self.db.commit()
        return education_translation_id
