import uuid
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from app.models.school.school_translation import SchoolTranslation

class SchoolTranslationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_school_translation(self, school: SchoolTranslation):
        school.id = str(uuid.uuid4())
        self.db.add(school)
        self.db.commit()
        self.db.refresh(school)
        return school

    def get_school_translation_by_school_id_and_language_id(self, school_id: str, language_id: str) -> SchoolTranslation:
        return self.db.query(SchoolTranslation).filter(SchoolTranslation.school_id == school_id, SchoolTranslation.language_id == language_id).first()

    def update_school_translation(self, school: SchoolTranslation):
        self.db.commit()
        return school

    def delete_school_translation(self, school_translation: SchoolTranslation) -> str:
        school_translation_id = school_translation.id
        self.db.delete(school_translation)
        self.db.commit()
        return school_translation_id
