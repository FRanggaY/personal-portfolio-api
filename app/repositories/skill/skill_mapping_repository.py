import uuid
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from app.models.skill.skill_mapping import SkillMapping

class SkillMappingRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_skill_mapping(self, skill_mapping: SkillMapping):
        skill_mapping.is_active = 1
        skill_mapping.id = str(uuid.uuid4())
        self.db.add(skill_mapping)
        self.db.commit()
        self.db.refresh(skill_mapping)
        return skill_mapping
    
    def read_skill_mappings(
        self, 
        sort_by: str = None, 
        sort_order: str = 'asc', 
        custom_filters: dict = None,
        offset: int = None, 
        size: int = None,
        is_active: bool = None,
    ) -> list[SkillMapping]:
        query = self.db.query(SkillMapping)

        # Filtering
        if is_active is not None:
            query = query.filter(SkillMapping.is_active == is_active)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(SkillMapping, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(SkillMapping, column) == value)

        # Sorting
        if sort_by is not None:
            if sort_order == 'asc' and hasattr(SkillMapping, sort_by):
                query = query.order_by(asc(getattr(SkillMapping, sort_by)))
            elif sort_order == 'desc' and hasattr(SkillMapping, sort_by):
                query = query.order_by(desc(getattr(SkillMapping, sort_by)))

        # Pagination
        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        return query.all()
    
    def count_skill_mappings(
        self, 
        custom_filters: dict = None,
        is_active: bool = None,
    ) -> int:
        query = self.db.query(SkillMapping)

        # Filtering
        if is_active is not None:
            query = query.filter(SkillMapping.is_active == is_active)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(SkillMapping, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(SkillMapping, column) == value)

        return query.count()

    def update_skill_mapping(self, skill_mapping: SkillMapping):
        self.db.commit()
        return skill_mapping

    def read_skill_mapping(self, id: str) -> SkillMapping:
        skill_mapping = self.db.query(SkillMapping).filter(SkillMapping.id == id).first()
        return skill_mapping
    
    def get_skill_mapping_by_personal(self, skill_id: str, user_id: str) -> SkillMapping:
        skill_mapping = self.db.query(SkillMapping).filter(SkillMapping.skill_id == skill_id, SkillMapping.user_id == user_id).first()
        return skill_mapping

    def delete_skill_mapping(self, skill_mapping: SkillMapping) -> str:
        skill_mapping_id = skill_mapping.id
        self.db.delete(skill_mapping)
        self.db.commit()
        return skill_mapping_id
