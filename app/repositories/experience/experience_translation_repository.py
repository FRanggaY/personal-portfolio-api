import uuid
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from app.models.experience.experience_translation import ExperienceTranslation

class ExperienceTranslationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_experience_translation(self, experience: ExperienceTranslation):
        experience.id = str(uuid.uuid4())
        self.db.add(experience)
        self.db.commit()
        self.db.refresh(experience)
        return experience

    def get_experience_translation_by_experience_id_and_language_id(self, experience_id: str, language_id: str) -> ExperienceTranslation:
        return self.db.query(ExperienceTranslation).filter(ExperienceTranslation.experience_id == experience_id, ExperienceTranslation.language_id == language_id).first()

    def update_experience_translation(self, experience: ExperienceTranslation):
        self.db.commit()
        return experience

    def delete_experience_translation(self, experience_translation: ExperienceTranslation) -> str:
        experience_translation_id = experience_translation.id
        self.db.delete(experience_translation)
        self.db.commit()
        return experience_translation_id
