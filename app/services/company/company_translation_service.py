from sqlalchemy.orm import Session

from app.models.company.company_translation import CompanyTranslation
from app.repositories.company.company_translation_repository import CompanyTranslationRepository

class CompanyTranslationService:
    def __init__(self, db: Session):
        self.db = db
        self.company_translation_repository = CompanyTranslationRepository(db)

    def update_company_translation(
        self, 
        exist_company_translation: CompanyTranslation, 
        company_translation: CompanyTranslation,
    ):
        
        exist_company_translation.name = company_translation.name
        exist_company_translation.description = company_translation.description
        exist_company_translation.address = company_translation.address

        return self.company_translation_repository.update_company_translation(exist_company_translation)
    
    def delete_company_translation(self, company_id: str, language_id: str):
        company_translation = self.company_translation_repository.get_company_translation_by_company_id_and_language_id(company_id, language_id)
        if not company_translation:
            raise ValueError("Company Translation not found")

        return self.company_translation_repository.delete_company_translation(company_translation)
