import uuid
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from app.models.skill.skill_translation import SkillTranslation

class SkillTranslationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_skill_translation(self, skill: SkillTranslation):
        skill.id = str(uuid.uuid4())
        self.db.add(skill)
        self.db.commit()
        self.db.refresh(skill)
        return skill

    def get_skill_translation_by_skill_id_and_language_id(self, skill_id: str, language_id: str) -> SkillTranslation:
        return self.db.query(SkillTranslation).filter(SkillTranslation.skill_id == skill_id, SkillTranslation.language_id == language_id).first()

    def update_skill_translation(self, skill: SkillTranslation):
        self.db.commit()
        return skill

    def delete_skill_translation(self, skill_translation: SkillTranslation) -> str:
        skill_translation_id = skill_translation.id
        self.db.delete(skill_translation)
        self.db.commit()
        return skill_translation_id
