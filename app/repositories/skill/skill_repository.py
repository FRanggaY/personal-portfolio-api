import uuid
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from app.models.skill.skill import Skill

class SkillRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_skill(self, skill: Skill):
        skill.is_active = 1
        skill.id = str(uuid.uuid4())
        self.db.add(skill)
        self.db.commit()
        self.db.refresh(skill)
        return skill

    def get_skill_by_name(self, name: str) -> Skill:
        return self.db.query(Skill).filter(Skill.name == name).first()
   
    def get_skill_by_code(self, code: str) -> Skill:
        return self.db.query(Skill).filter(Skill.code == code).first()
    
    def read_skills(
        self, 
        sort_by: str = None, 
        sort_order: str = 'asc', 
        custom_filters: dict = None,
        offset: int = None, 
        size: int = None,
        is_active: bool = None,
    ) -> list[Skill]:
        query = self.db.query(Skill)

        # Filtering
        if is_active is not None:
            query = query.filter(Skill.is_active == is_active)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(Skill, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(Skill, column) == value)

        # Sorting
        if sort_by is not None:
            if sort_order == 'asc' and hasattr(Skill, sort_by):
                query = query.order_by(asc(getattr(Skill, sort_by)))
            elif sort_order == 'desc' and hasattr(Skill, sort_by):
                query = query.order_by(desc(getattr(Skill, sort_by)))

        # Pagination
        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        return query.all()
    
    def count_skills(
        self, 
        custom_filters: dict = None,
        is_active: bool = None,
    ) -> int:
        query = self.db.query(Skill)

        # Filtering
        if is_active is not None:
            query = query.filter(Skill.is_active == is_active)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(Skill, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(Skill, column) == value)

        return query.count()

    def update_skill(self, skill: Skill):
        self.db.commit()
        return skill

    def read_skill(self, id: str) -> Skill:
        skill = self.db.query(Skill).filter(Skill.id == id).first()
        return skill

    def delete_skill(self, skill: Skill) -> str:
        skill_id = skill.id
        self.db.delete(skill)
        self.db.commit()
        return skill_id
