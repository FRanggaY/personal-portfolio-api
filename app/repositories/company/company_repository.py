import uuid
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from app.models.company.company import Company

class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_company(self, company: Company):
        company.is_active = 1
        company.id = str(uuid.uuid4())
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def get_company_by_name(self, name: str) -> Company:
        return self.db.query(Company).filter(Company.name == name).first()
   
    def get_company_by_code(self, code: str) -> Company:
        return self.db.query(Company).filter(Company.code == code).first()
    
    def read_companies(
        self, 
        sort_by: str = None, 
        sort_order: str = 'asc', 
        custom_filters: dict = None,
        offset: int = None, 
        size: int = None,
        is_active: bool = None,
    ) -> list[Company]:
        query = self.db.query(Company)

        # Filtering
        if is_active is not None:
            query = query.filter(Company.is_active == is_active)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(Company, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(Company, column) == value)

        # Sorting
        if sort_by is not None:
            if sort_order == 'asc' and hasattr(Company, sort_by):
                query = query.order_by(asc(getattr(Company, sort_by)))
            elif sort_order == 'desc' and hasattr(Company, sort_by):
                query = query.order_by(desc(getattr(Company, sort_by)))

        # Pagination
        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        return query.all()
    
    def count_companies(
        self, 
        custom_filters: dict = None,
        is_active: bool = None,
    ) -> int:
        query = self.db.query(Company)

        # Filtering
        if is_active is not None:
            query = query.filter(Company.is_active == is_active)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(Company, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(Company, column) == value)

        return query.count()

    def update_company(self, company: Company):
        self.db.commit()
        return company

    def read_company(self, id: str) -> Company:
        company = self.db.query(Company).filter(Company.id == id).first()
        return company

    def delete_company(self, company: Company) -> str:
        company_id = company.id
        self.db.delete(company)
        self.db.commit()
        return company_id
