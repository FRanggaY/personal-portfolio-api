import uuid
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from app.models.project.project_skill import ProjectSkill

class ProjectSkillRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_project_skill(self, project: ProjectSkill):
        project.id = str(uuid.uuid4())
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def get_project_skill_by_project_id_and_skill_id(self, project_id: str, skill_id: str) -> ProjectSkill:
        return self.db.query(ProjectSkill).filter(ProjectSkill.project_id == project_id, ProjectSkill.skill_id == skill_id).first()

    def read_project_skills(
        self, 
        sort_by: str = None, 
        sort_order: str = 'asc', 
        custom_filters: dict = None,
        offset: int = None, 
        size: int = None,
        is_active: bool = None,
        project_id: str = None,
    ) -> list[ProjectSkill]:
        query = self.db.query(ProjectSkill)

        # Filtering
        if is_active is not None:
            query = query.filter(ProjectSkill.is_active == is_active)
       
        if project_id is not None:
            query = query.filter(ProjectSkill.project_id == project_id)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(ProjectSkill, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(ProjectSkill, column) == value)

        # Sorting
        if sort_by is not None:
            if sort_order == 'asc' and hasattr(ProjectSkill, sort_by):
                query = query.order_by(asc(getattr(ProjectSkill, sort_by)))
            elif sort_order == 'desc' and hasattr(ProjectSkill, sort_by):
                query = query.order_by(desc(getattr(ProjectSkill, sort_by)))

        # Pagination
        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        return query.all()
    
    def count_project_skills(
        self, 
        custom_filters: dict = None,
        is_active: bool = None,
        project_id: str = None,
    ) -> int:
        query = self.db.query(ProjectSkill)

        # Filtering
        if is_active is not None:
            query = query.filter(ProjectSkill.is_active == is_active)
        
        if project_id is not None:
            query = query.filter(ProjectSkill.project_id == project_id)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(ProjectSkill, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(ProjectSkill, column) == value)

        return query.count()

    def update_project_skill(self, project: ProjectSkill):
        self.db.commit()
        return project

    def delete_project_skill(self, project_skill: ProjectSkill) -> str:
        project_skill_id = project_skill.id
        self.db.delete(project_skill)
        self.db.commit()
        return project_skill_id
