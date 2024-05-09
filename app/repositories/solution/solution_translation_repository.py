import uuid
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from app.models.solution.solution import Solution
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

    def get_solution_translation_by_user_id_and_language_id(
        self, 
        user_id: str, 
        language_id: str,
        sort_by: str = None, 
        sort_order: str = 'asc', 
        custom_filters: dict = None,
        offset: int = None, 
        size: int = None, 
    ) -> list[SolutionTranslation]:
        query = self.db.query(SolutionTranslation) \
            .join(Solution, SolutionTranslation.solution_id == Solution.id)
        
        query = query.filter(Solution.user_id == user_id)
        query = query.filter(SolutionTranslation.language_id == language_id)

        query = query.filter(Solution.is_active == True)

         # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(SolutionTranslation, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(SolutionTranslation, column) == value)

        # Sorting
        if sort_by is not None:
            if sort_order == 'asc' and hasattr(SolutionTranslation, sort_by):
                query = query.order_by(asc(getattr(SolutionTranslation, sort_by)))
            elif sort_order == 'desc' and hasattr(SolutionTranslation, sort_by):
                query = query.order_by(desc(getattr(SolutionTranslation, sort_by)))

        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        return query.all()
    
    def count_solution_translation_by_user_id_and_language_id(
        self, 
        user_id: str, 
        language_id: str,
        custom_filters: dict = None,
    ) -> list[SolutionTranslation]:
        query = self.db.query(SolutionTranslation) \
            .join(Solution, SolutionTranslation.solution_id == Solution.id)
        
        query = query.filter(Solution.user_id == user_id)
        query = query.filter(SolutionTranslation.language_id == language_id)

        query = query.filter(Solution.is_active == True)

         # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(SolutionTranslation, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(SolutionTranslation, column) == value)

        return query.count()

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
