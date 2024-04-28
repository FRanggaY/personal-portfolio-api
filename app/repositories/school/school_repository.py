import uuid
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from app.models.school.school import School

class SchoolRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_school(self, school: School):
        school.is_active = 1
        school.id = str(uuid.uuid4())
        self.db.add(school)
        self.db.commit()
        self.db.refresh(school)
        return school

    def get_school_by_name(self, name: str) -> School:
        return self.db.query(School).filter(School.name == name).first()
   
    def get_school_by_code(self, code: str) -> School:
        return self.db.query(School).filter(School.code == code).first()
    
    def read_schools(
        self, 
        sort_by: str = None, 
        sort_order: str = 'asc', 
        custom_filters: dict = None,
        offset: int = None, 
        size: int = None,
        is_active: bool = None,
    ) -> list[School]:
        query = self.db.query(School)

        # Filtering
        if is_active is not None:
            query = query.filter(School.is_active == is_active)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(School, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(School, column) == value)

        # Sorting
        if sort_by is not None:
            if sort_order == 'asc' and hasattr(School, sort_by):
                query = query.order_by(asc(getattr(School, sort_by)))
            elif sort_order == 'desc' and hasattr(School, sort_by):
                query = query.order_by(desc(getattr(School, sort_by)))

        # Pagination
        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        return query.all()
    
    def count_schools(
        self, 
        custom_filters: dict = None,
        is_active: bool = None,
    ) -> int:
        query = self.db.query(School)

        # Filtering
        if is_active is not None:
            query = query.filter(School.is_active == is_active)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(School, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(School, column) == value)

        return query.count()

    def update_school(self, school: School):
        self.db.commit()
        return school

    def read_school(self, id: str) -> School:
        school = self.db.query(School).filter(School.id == id).first()
        return school

    def delete_school(self, school: School) -> str:
        school_id = school.id
        self.db.delete(school)
        self.db.commit()
        return school_id
