import uuid
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from app.models.skill.skill_mapping import SkillMapping
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

    def get_skill_translation_by_user_id_and_language_id(
        self, 
        user_id: str, 
        language_id: str,
        sort_by: str = None, 
        sort_order: str = 'asc', 
        custom_filters: dict = None,
        offset: int = None, 
        size: int = None, 
    ) -> list[SkillTranslation]:
        query = self.db.query(SkillTranslation).join(SkillMapping, SkillTranslation.skill_id == SkillMapping.skill_id)
        
        query = query.filter(SkillMapping.user_id == user_id)
        query = query.filter(SkillTranslation.language_id == language_id)

        query = query.filter(SkillMapping.is_active == True)

         # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(SkillTranslation, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(SkillTranslation, column) == value)

        # Sorting
        if sort_by is not None:
            if sort_order == 'asc' and hasattr(SkillTranslation, sort_by):
                query = query.order_by(asc(getattr(SkillTranslation, sort_by)))
            elif sort_order == 'desc' and hasattr(SkillTranslation, sort_by):
                query = query.order_by(desc(getattr(SkillTranslation, sort_by)))

        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        return query.all()
    
    def count_skill_translation_by_user_id_and_language_id(
        self, 
        user_id: str, 
        language_id: str,
        custom_filters: dict = None,
    ) -> list[SkillTranslation]:
        query = self.db.query(SkillTranslation).join(SkillMapping, SkillTranslation.skill_id == SkillMapping.skill_id)
        
        query = query.filter(SkillMapping.user_id == user_id)
        query = query.filter(SkillTranslation.language_id == language_id)

        query = query.filter(SkillMapping.is_active == True)

         # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(SkillTranslation, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(SkillTranslation, column) == value)

        return query.count()
    
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
