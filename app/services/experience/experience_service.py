from sqlalchemy.orm import Session

from app.models.experience.experience import Experience
from app.repositories.experience.experience_repository import ExperienceRepository

class ExperienceService:
    def __init__(self, db: Session):
        self.db = db
        self.experience_repository = ExperienceRepository(db)

    def update_experience(
        self, 
        exist_experience: Experience, 
        experience: Experience,
    ):
        
        exist_experience.title = experience.title
        exist_experience.started_at = experience.started_at
        exist_experience.finished_at = experience.finished_at
        exist_experience.is_active = experience.is_active

        return self.experience_repository.update_experience(exist_experience)
    
    def delete_experience(self, experience_id: str):
        experience = self.experience_repository.read_experience(experience_id)
        if not experience:
            raise ValueError("Experience not found")
        
        return self.experience_repository.delete_experience(experience)
