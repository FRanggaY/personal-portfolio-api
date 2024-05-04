import uuid
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from app.models.project.project_attachment import ProjectAttachment

class ProjectAttachmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_project_attachment(self, project_attachment: ProjectAttachment):
        project_attachment.is_active = 1
        project_attachment.id = str(uuid.uuid4())
        self.db.add(project_attachment)
        self.db.commit()
        self.db.refresh(project_attachment)
        return project_attachment
    
    def read_project_attachments(
        self, 
        sort_by: str = None, 
        sort_order: str = 'asc', 
        custom_filters: dict = None,
        offset: int = None, 
        size: int = None,
        is_active: bool = None,
        project_id: str = None,
    ) -> list[ProjectAttachment]:
        query = self.db.query(ProjectAttachment)

        # Filtering
        if is_active is not None:
            query = query.filter(ProjectAttachment.is_active == is_active)
       
        if project_id is not None:
            query = query.filter(ProjectAttachment.project_id == project_id)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(ProjectAttachment, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(ProjectAttachment, column) == value)

        # Sorting
        if sort_by is not None:
            if sort_order == 'asc' and hasattr(ProjectAttachment, sort_by):
                query = query.order_by(asc(getattr(ProjectAttachment, sort_by)))
            elif sort_order == 'desc' and hasattr(ProjectAttachment, sort_by):
                query = query.order_by(desc(getattr(ProjectAttachment, sort_by)))

        # Pagination
        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        return query.all()
    
    def count_project_attachments(
        self, 
        custom_filters: dict = None,
        is_active: bool = None,
        project_id: str = None,
    ) -> int:
        query = self.db.query(ProjectAttachment)

        # Filtering
        if is_active is not None:
            query = query.filter(ProjectAttachment.is_active == is_active)
        
        if project_id is not None:
            query = query.filter(ProjectAttachment.project_id == project_id)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(ProjectAttachment, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(ProjectAttachment, column) == value)

        return query.count()

    def update_project_attachment(self, project_attachment: ProjectAttachment):
        self.db.commit()
        return project_attachment

    def read_project_attachment(self, id: str) -> ProjectAttachment:
        project_attachment = self.db.query(ProjectAttachment).filter(ProjectAttachment.id == id).first()
        return project_attachment

    def delete_project_attachment(self, project_attachment: ProjectAttachment) -> str:
        project_attachment_id = project_attachment.id
        self.db.delete(project_attachment)
        self.db.commit()
        return project_attachment_id
