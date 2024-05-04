import uuid
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from app.models.education.education import Education

class EducationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_education(self, education: Education):
        education.is_active = 1
        education.id = str(uuid.uuid4())
        self.db.add(education)
        self.db.commit()
        self.db.refresh(education)
        return education
    
    def read_educations(
        self, 
        sort_by: str = None, 
        sort_order: str = 'asc', 
        custom_filters: dict = None,
        offset: int = None, 
        size: int = None,
        is_active: bool = None,
        user_id: str = None,
    ) -> list[Education]:
        query = self.db.query(Education)

        # Filtering
        if is_active is not None:
            query = query.filter(Education.is_active == is_active)
        
        if user_id is not None:
            query = query.filter(Education.user_id == user_id)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(Education, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(Education, column) == value)

        # Sorting
        if sort_by is not None:
            if sort_order == 'asc' and hasattr(Education, sort_by):
                query = query.order_by(asc(getattr(Education, sort_by)))
            elif sort_order == 'desc' and hasattr(Education, sort_by):
                query = query.order_by(desc(getattr(Education, sort_by)))

        # Pagination
        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        return query.all()
    
    def count_educations(
        self, 
        custom_filters: dict = None,
        is_active: bool = None,
        user_id: str = None,
    ) -> int:
        query = self.db.query(Education)

        # Filtering
        if is_active is not None:
            query = query.filter(Education.is_active == is_active)

        if user_id is not None:
            query = query.filter(Education.user_id == user_id)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(Education, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(Education, column) == value)

        return query.count()

    def update_education(self, education: Education):
        self.db.commit()
        return education

    def read_education(self, id: str) -> Education:
        education = self.db.query(Education).filter(Education.id == id).first()
        return education

    def delete_education(self, education: Education) -> str:
        education_id = education.id
        self.db.delete(education)
        self.db.commit()
        return education_id
