import uuid
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from app.models.project.project import Project

class ProjectRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_project(self, project: Project):
        project.is_active = 1
        project.id = str(uuid.uuid4())
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def read_projects(
        self, 
        sort_by: str = None, 
        sort_order: str = 'asc', 
        custom_filters: dict = None,
        offset: int = None, 
        size: int = None,
        is_active: bool = None,
        user_id: str = None,
    ) -> list[Project]:
        query = self.db.query(Project)

        # Filtering
        if is_active is not None:
            query = query.filter(Project.is_active == is_active)

        if user_id is not None:
            query = query.filter(Project.user_id == user_id)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(Project, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(Project, column) == value)

        # Sorting
        if sort_by is not None:
            if sort_order == 'asc' and hasattr(Project, sort_by):
                query = query.order_by(asc(getattr(Project, sort_by)))
            elif sort_order == 'desc' and hasattr(Project, sort_by):
                query = query.order_by(desc(getattr(Project, sort_by)))

        # Pagination
        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        return query.all()
    
    def count_projects(
        self, 
        custom_filters: dict = None,
        is_active: bool = None,
        user_id: str = None,
    ) -> int:
        query = self.db.query(Project)

        # Filtering
        if is_active is not None:
            query = query.filter(Project.is_active == is_active)
        
        if user_id is not None:
            query = query.filter(Project.user_id == user_id)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(Project, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(Project, column) == value)

        return query.count()

    def update_project(self, project: Project):
        self.db.commit()
        return project

    def read_project(self, id: str) -> Project:
        project = self.db.query(Project).filter(Project.id == id).first()
        return project

    def delete_project(self, project: Project) -> str:
        project_id = project.id
        self.db.delete(project)
        self.db.commit()
        return project_id
