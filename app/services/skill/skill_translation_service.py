from sqlalchemy.orm import Session

from app.models.skill.skill_translation import SkillTranslation
from app.repositories.skill.skill_translation_repository import SkillTranslationRepository

class SkillTranslationService:
    def __init__(self, db: Session):
        self.db = db
        self.skill_translation_repository = SkillTranslationRepository(db)

    def update_skill_translation(
        self, 
        exist_skill_translation: SkillTranslation, 
        skill_translation: SkillTranslation,
    ):
        
        exist_skill_translation.name = skill_translation.name
        exist_skill_translation.description = skill_translation.description

        return self.skill_translation_repository.update_skill_translation(exist_skill_translation)
    
    def delete_skill_translation(self, skill_id: str, language_id: str):
        skill_translation = self.skill_translation_repository.get_skill_translation_by_skill_id_and_language_id(skill_id, language_id)
        if not skill_translation:
            raise ValueError("Skill Translation not found")

        return self.skill_translation_repository.delete_skill_translation(skill_translation)
