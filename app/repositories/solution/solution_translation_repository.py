import uuid
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from app.models.solution.solution_translation import SolutionTranslation

class SolutionTranslationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_solution_translation(self, solution: SolutionTranslation):
        solution.id = str(uuid.uuid4())
        self.db.add(solution)
        self.db.commit()
        self.db.refresh(solution)
        return solution

    def get_solution_translation_by_solution_id_and_language_id(self, solution_id: str, language_id: str) -> SolutionTranslation:
        return self.db.query(SolutionTranslation).filter(SolutionTranslation.solution_id == solution_id, SolutionTranslation.language_id == language_id).first()

    def update_solution_translation(self, solution: SolutionTranslation):
        self.db.commit()
        return solution

    def delete_solution_translation(self, solution_translation: SolutionTranslation) -> str:
        solution_translation_id = solution_translation.id
        self.db.delete(solution_translation)
        self.db.commit()
        return solution_translation_id
