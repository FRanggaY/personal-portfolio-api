import uuid
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from app.models.experience.experience import Experience

class ExperienceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_experience(self, experience: Experience):
        experience.is_active = 1
        experience.id = str(uuid.uuid4())
        self.db.add(experience)
        self.db.commit()
        self.db.refresh(experience)
        return experience
    
    def read_experiences(
        self, 
        sort_by: str = None, 
        sort_order: str = 'asc', 
        custom_filters: dict = None,
        offset: int = None, 
        size: int = None,
        is_active: bool = None,
        user_id: str = None,
    ) -> list[Experience]:
        query = self.db.query(Experience)

        # Filtering
        if is_active is not None:
            query = query.filter(Experience.is_active == is_active)

        if user_id is not None:
            query = query.filter(Experience.user_id == user_id)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(Experience, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(Experience, column) == value)

        # Sorting
        if sort_by is not None:
            if sort_order == 'asc' and hasattr(Experience, sort_by):
                query = query.order_by(asc(getattr(Experience, sort_by)))
            elif sort_order == 'desc' and hasattr(Experience, sort_by):
                query = query.order_by(desc(getattr(Experience, sort_by)))

        # Pagination
        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        return query.all()
    
    def count_experiences(
        self, 
        custom_filters: dict = None,
        is_active: bool = None,
        user_id: str = None,
    ) -> int:
        query = self.db.query(Experience)

        # Filtering
        if is_active is not None:
            query = query.filter(Experience.is_active == is_active)
        
        if user_id is not None:
            query = query.filter(Experience.user_id == user_id)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(Experience, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(Experience, column) == value)

        return query.count()

    def update_experience(self, experience: Experience):
        self.db.commit()
        return experience

    def read_experience(self, id: str) -> Experience:
        experience = self.db.query(Experience).filter(Experience.id == id).first()
        return experience

    def delete_experience(self, experience: Experience) -> str:
        experience_id = experience.id
        self.db.delete(experience)
        self.db.commit()
        return experience_id
