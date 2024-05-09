import uuid
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from app.models.project.project import Project
from app.models.project.project_translation import ProjectTranslation

class ProjectTranslationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_project_translation(self, project: ProjectTranslation):
        project.id = str(uuid.uuid4())
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project
    
    def get_project_translation_by_user_id_and_language_id(
        self, 
        user_id: str, 
        language_id: str,
        sort_by: str = None, 
        sort_order: str = 'asc', 
        custom_filters: dict = None,
        offset: int = None, 
        size: int = None, 
    ) -> list[ProjectTranslation]:
        query = self.db.query(ProjectTranslation) \
            .join(Project, ProjectTranslation.project_id == Project.id)
        
        query = query.filter(Project.user_id == user_id)
        query = query.filter(ProjectTranslation.language_id == language_id)

        query = query.filter(Project.is_active == True)

         # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(ProjectTranslation, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(ProjectTranslation, column) == value)

        # Sorting
        if sort_by is not None:
            if sort_order == 'asc' and hasattr(ProjectTranslation, sort_by):
                query = query.order_by(asc(getattr(ProjectTranslation, sort_by)))
            elif sort_order == 'desc' and hasattr(ProjectTranslation, sort_by):
                query = query.order_by(desc(getattr(ProjectTranslation, sort_by)))

        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        return query.all()
    
    def count_project_translation_by_user_id_and_language_id(
        self, 
        user_id: str, 
        language_id: str,
        custom_filters: dict = None,
    ) -> list[ProjectTranslation]:
        query = self.db.query(ProjectTranslation) \
            .join(Project, ProjectTranslation.project_id == Project.id)
        
        query = query.filter(Project.user_id == user_id)
        query = query.filter(ProjectTranslation.language_id == language_id)

        query = query.filter(Project.is_active == True)

         # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(ProjectTranslation, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(ProjectTranslation, column) == value)

        return query.count()


    def get_project_translation_by_project_id_and_language_id(self, project_id: str, language_id: str) -> ProjectTranslation:
        return self.db.query(ProjectTranslation).filter(ProjectTranslation.project_id == project_id, ProjectTranslation.language_id == language_id).first()

    def update_project_translation(self, project: ProjectTranslation):
        self.db.commit()
        return project

    def delete_project_translation(self, project_translation: ProjectTranslation) -> str:
        project_translation_id = project_translation.id
        self.db.delete(project_translation)
        self.db.commit()
        return project_translation_id
