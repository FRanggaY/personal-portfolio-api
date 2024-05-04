from sqlalchemy.orm import Session

from app.models.education.education import Education
from app.repositories.education.education_repository import EducationRepository

class EducationService:
    def __init__(self, db: Session):
        self.db = db
        self.education_repository = EducationRepository(db)

    def update_education(
        self, 
        exist_education: Education, 
        education: Education,
    ):
        
        exist_education.title = education.title
        exist_education.started_at = education.started_at
        exist_education.finished_at = education.finished_at
        exist_education.is_active = education.is_active

        return self.education_repository.update_education(exist_education)