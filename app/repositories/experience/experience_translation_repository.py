import uuid
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from app.models.company.company import Company
from app.models.company.company_translation import CompanyTranslation
from app.models.experience.experience import Experience
from app.models.experience.experience_translation import ExperienceTranslation

class ExperienceTranslationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_experience_translation(self, experience: ExperienceTranslation):
        experience.id = str(uuid.uuid4())
        self.db.add(experience)
        self.db.commit()
        self.db.refresh(experience)
        return experience
    
    def get_experience_translation_by_user_id_and_language_id(
        self, 
        user_id: str, 
        language_id: str,
        sort_by: str = None, 
        sort_order: str = 'asc', 
        custom_filters: dict = None,
        offset: int = None, 
        size: int = None, 
    ) -> list[ExperienceTranslation]:
        query = self.db.query(ExperienceTranslation) \
            .join(Experience, ExperienceTranslation.experience_id == Experience.id) \
            .join(Company, Experience.company_id == Company.id) \
            .join(CompanyTranslation, Company.id == CompanyTranslation.company_id) \
        
        query = query.filter(Experience.user_id == user_id)
        query = query.filter(ExperienceTranslation.language_id == language_id)
        query = query.filter(CompanyTranslation.language_id == language_id)

        query = query.filter(Experience.is_active == True)

         # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(ExperienceTranslation, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(ExperienceTranslation, column) == value)

        # Sorting
        if sort_by is not None:
            if sort_order == 'asc' and hasattr(ExperienceTranslation, sort_by):
                query = query.order_by(asc(getattr(ExperienceTranslation, sort_by)))
            elif sort_order == 'desc' and hasattr(ExperienceTranslation, sort_by):
                query = query.order_by(desc(getattr(ExperienceTranslation, sort_by)))

        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        return query.all()
    
    def count_experience_translation_by_user_id_and_language_id(
        self, 
        user_id: str, 
        language_id: str,
        custom_filters: dict = None,
    ) -> list[ExperienceTranslation]:
        query = self.db.query(ExperienceTranslation) \
            .join(Experience, ExperienceTranslation.experience_id == Experience.id) \
            .join(Company, Experience.company_id == Company.id) \
            .join(CompanyTranslation, Company.id == CompanyTranslation.company_id) \
        
        query = query.filter(Experience.user_id == user_id)
        query = query.filter(ExperienceTranslation.language_id == language_id)
        query = query.filter(CompanyTranslation.language_id == language_id)

        query = query.filter(Experience.is_active == True)

         # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(ExperienceTranslation, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(ExperienceTranslation, column) == value)

        return query.count()

    def get_experience_translation_by_experience_id_and_language_id(self, experience_id: str, language_id: str) -> ExperienceTranslation:
        return self.db.query(ExperienceTranslation).filter(ExperienceTranslation.experience_id == experience_id, ExperienceTranslation.language_id == language_id).first()

    def update_experience_translation(self, experience: ExperienceTranslation):
        self.db.commit()
        return experience

    def delete_experience_translation(self, experience_translation: ExperienceTranslation) -> str:
        experience_translation_id = experience_translation.id
        self.db.delete(experience_translation)
        self.db.commit()
        return experience_translation_id
