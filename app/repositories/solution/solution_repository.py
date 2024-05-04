import uuid
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from app.models.solution.solution import Solution

class SolutionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_solution(self, solution: Solution):
        solution.is_active = 1
        solution.id = str(uuid.uuid4())
        self.db.add(solution)
        self.db.commit()
        self.db.refresh(solution)
        return solution
    
    def read_solutions(
        self, 
        sort_by: str = None, 
        sort_order: str = 'asc', 
        custom_filters: dict = None,
        offset: int = None, 
        size: int = None,
        is_active: bool = None,
        user_id: str = None,
    ) -> list[Solution]:
        query = self.db.query(Solution)

        # Filtering
        if is_active is not None:
            query = query.filter(Solution.is_active == is_active)

        if user_id is not None:
            query = query.filter(Solution.user_id == user_id)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(Solution, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(Solution, column) == value)

        # Sorting
        if sort_by is not None:
            if sort_order == 'asc' and hasattr(Solution, sort_by):
                query = query.order_by(asc(getattr(Solution, sort_by)))
            elif sort_order == 'desc' and hasattr(Solution, sort_by):
                query = query.order_by(desc(getattr(Solution, sort_by)))

        # Pagination
        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        return query.all()
    
    def count_solutions(
        self, 
        custom_filters: dict = None,
        is_active: bool = None,
        user_id: str = None,
    ) -> int:
        query = self.db.query(Solution)

        # Filtering
        if is_active is not None:
            query = query.filter(Solution.is_active == is_active)
        
        if user_id is not None:
            query = query.filter(Solution.user_id == user_id)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(Solution, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(Solution, column) == value)

        return query.count()

    def update_solution(self, solution: Solution):
        self.db.commit()
        return solution

    def read_solution(self, id: str) -> Solution:
        solution = self.db.query(Solution).filter(Solution.id == id).first()
        return solution

    def delete_solution(self, solution: Solution) -> str:
        solution_id = solution.id
        self.db.delete(solution)
        self.db.commit()
        return solution_id
