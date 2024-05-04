from sqlalchemy.orm import Session

from app.models.skill.skill_mapping import SkillMapping
from app.repositories.skill.skill_mapping_repository import SkillMappingRepository

class SkillMappingService:
    def __init__(self, db: Session):
        self.db = db
        self.skill_mapping_repository = SkillMappingRepository(db)

    def update_skill_mapping(
        self, 
        exist_skill_mapping: SkillMapping, 
        skill_mapping: SkillMapping,
    ):
        exist_skill_mapping.is_active = skill_mapping.is_active

        return self.skill_mapping_repository.update_skill_mapping(exist_skill_mapping)
