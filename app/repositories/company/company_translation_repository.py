import uuid
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from app.models.company.company_translation import CompanyTranslation

class CompanyTranslationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_company_translation(self, company: CompanyTranslation):
        company.id = str(uuid.uuid4())
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)
        return company

    def get_company_translation_by_company_id_and_language_id(self, company_id: str, language_id: str) -> CompanyTranslation:
        return self.db.query(CompanyTranslation).filter(CompanyTranslation.company_id == company_id, CompanyTranslation.language_id == language_id).first()

    def update_company_translation(self, company: CompanyTranslation):
        self.db.commit()
        return company

    def delete_company_translation(self, company_translation: CompanyTranslation) -> str:
        company_translation_id = company_translation.id
        self.db.delete(company_translation)
        self.db.commit()
        return company_translation_id
