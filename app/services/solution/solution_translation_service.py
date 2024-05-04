from sqlalchemy.orm import Session

from app.models.solution.solution_translation import SolutionTranslation
from app.repositories.solution.solution_translation_repository import SolutionTranslationRepository

class SolutionTranslationService:
    def __init__(self, db: Session):
        self.db = db
        self.solution_translation_repository = SolutionTranslationRepository(db)

    def update_solution_translation(
        self, 
        exist_solution_translation: SolutionTranslation, 
        solution_translation: SolutionTranslation,
    ):
        
        exist_solution_translation.title = solution_translation.title
        exist_solution_translation.description = solution_translation.description

        return self.solution_translation_repository.update_solution_translation(exist_solution_translation)