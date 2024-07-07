import uuid
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from app.models.education.education import Education
from app.models.education.education_translation import EducationTranslation
from app.models.school.school import School
from app.models.school.school_translation import SchoolTranslation

class EducationTranslationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_education_translation(self, education: EducationTranslation):
        education.id = str(uuid.uuid4())
        self.db.add(education)
        self.db.commit()
        self.db.refresh(education)
        return education
    
    def get_education_translation_by_user_id_and_language_id(
        self, 
        user_id: str, 
        language_id: str,
        sort_by: str = None, 
        sort_order: str = 'asc', 
        custom_filters: dict = None,
        offset: int = None, 
        size: int = None, 
    ) -> list[EducationTranslation]:
        query = self.db.query(EducationTranslation) \
            .join(Education, EducationTranslation.education_id == Education.id) \
            .join(School, Education.school_id == School.id) \
            .join(SchoolTranslation, School.id == SchoolTranslation.school_id) \
        
        query = query.filter(Education.user_id == user_id)
        query = query.filter(EducationTranslation.language_id == language_id)
        query = query.filter(SchoolTranslation.language_id == language_id)

        query = query.filter(Education.is_active == True)

         # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(EducationTranslation, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(EducationTranslation, column) == value)

        # Sorting
        if sort_by is not None:
            if sort_order == 'asc' and hasattr(EducationTranslation, sort_by):
                query = query.order_by(asc(getattr(EducationTranslation, sort_by)))
            elif sort_order == 'desc' and hasattr(EducationTranslation, sort_by):
                query = query.order_by(desc(getattr(EducationTranslation, sort_by)))
            elif sort_order == 'asc' and hasattr(Education, sort_by):
                query = query.order_by(asc(getattr(Education, sort_by)))
            elif sort_order == 'desc' and hasattr(Education, sort_by):
                query = query.order_by(desc(getattr(Education, sort_by)))

        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        return query.all()
    
    def count_education_translation_by_user_id_and_language_id(
        self, 
        user_id: str, 
        language_id: str,
        custom_filters: dict = None,
    ) -> list[EducationTranslation]:
        query = self.db.query(EducationTranslation) \
            .join(Education, EducationTranslation.education_id == Education.id) \
            .join(School, Education.school_id == School.id) \
            .join(SchoolTranslation, School.id == SchoolTranslation.school_id) \
        
        query = query.filter(Education.user_id == user_id)
        query = query.filter(EducationTranslation.language_id == language_id)
        query = query.filter(SchoolTranslation.language_id == language_id)

        query = query.filter(Education.is_active == True)

         # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(EducationTranslation, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(EducationTranslation, column) == value)

        return query.count()

    def get_education_translation_by_education_id_and_language_id(self, education_id: str, language_id: str) -> EducationTranslation:
        return self.db.query(EducationTranslation).filter(EducationTranslation.education_id == education_id, EducationTranslation.language_id == language_id).first()

    def update_education_translation(self, education: EducationTranslation):
        self.db.commit()
        return education

    def delete_education_translation(self, education_translation: EducationTranslation) -> str:
        education_translation_id = education_translation.id
        self.db.delete(education_translation)
        self.db.commit()
        return education_translation_id
