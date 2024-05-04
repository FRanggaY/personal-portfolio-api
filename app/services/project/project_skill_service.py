from sqlalchemy.orm import Session

from app.models.project.project_skill import ProjectSkill
from app.repositories.project.project_skill_repository import ProjectSkillRepository

class ProjectSkillService:
    def __init__(self, db: Session):
        self.db = db
        self.project_skill_repository = ProjectSkillRepository(db)

    def update_project_skill(
        self, 
        exist_project_skill: ProjectSkill, 
        project_skill: ProjectSkill,
    ):
        
        exist_project_skill.is_active = project_skill.is_active

        return self.project_skill_repository.update_project_skill(exist_project_skill)