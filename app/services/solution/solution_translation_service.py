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
    
    def delete_solution_translation(self, solution_id: str, language_id: str):
        solution_translation = self.solution_translation_repository.get_solution_translation_by_solution_id_and_language_id(solution_id, language_id)
        if not solution_translation:
            raise ValueError("Solution Translation not found")

        return self.solution_translation_repository.delete_solution_translation(solution_translation)