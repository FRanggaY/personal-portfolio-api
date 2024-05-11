import os
import uuid
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.company.company import Company
from app.repositories.company.company_repository import CompanyRepository
from app.utils.handling_file import delete_file, upload_file

class CompanyService:
    def __init__(self, db: Session):
        self.db = db
        self.company_repository = CompanyRepository(db)
        self.static_folder_image = "static/images/company/image"
        self.static_folder_logo = "static/images/company/logo"
    
    def create_company(self, company: Company, image: UploadFile = None, logo: UploadFile = None, file_extension_image = None, file_extension_logo = None):
        company.image_url = upload_file(image, self.static_folder_image, file_extension_image, company.code) if image else ''
        company.logo_url = upload_file(logo, self.static_folder_logo, file_extension_logo, company.code) if logo else ''

        return self.company_repository.create_company(company)
    
    def validation_unique_based_other_company(self, exist_company: Company, company: Company):
        if company.code:
            exist_code = self.company_repository.get_company_by_code(company.code)
            if exist_code and (exist_company.id != exist_code.id):
                raise ValueError('Code already used in other account')
            exist_company.code = company.code
        
        if company.name:
            exist_name = self.company_repository.get_company_by_name(company.name)
            if exist_name and (exist_company.id != exist_name.id):
                raise ValueError('Name already used in other account')
            exist_company.name = company.name

    def update_company(
        self, 
        exist_company: Company, 
        company: Company, 
        image: UploadFile = None,
        logo: UploadFile = None,
        file_extension_image = None,
        file_extension_logo = None,
    ):
        self.validation_unique_based_other_company(exist_company, company)
        
        exist_company.website_url = company.website_url
        exist_company.is_active = company.is_active

        if image and exist_company.image_url:
            file_path = os.path.join(self.static_folder_image, exist_company.image_url)
            delete_file(file_path)
            exist_company.image_url = upload_file(image, self.static_folder_image, file_extension_image, company.code)
        
        if image and not exist_company.image_url:
            exist_company.image_url = upload_file(image, self.static_folder_image, file_extension_image, company.code)

        if logo and exist_company.logo_url:
            file_path = os.path.join(self.static_folder_logo, exist_company.logo_url)
            delete_file(file_path)
            exist_company.logo_url = upload_file(logo, self.static_folder_logo, file_extension_logo, company.code)

        if logo and not exist_company.logo_url:
            exist_company.logo_url = upload_file(logo, self.static_folder_logo, file_extension_logo, company.code)


        return self.company_repository.update_company(exist_company)
    
    def delete_company(self, company_id: str):
        company = self.company_repository.read_company(company_id)
        if not company:
            raise ValueError("Company not found")

        if company.image_url:
            file_path = os.path.join(self.static_folder_image, company.image_url)
            delete_file(file_path)

        if company.logo_url:
            file_path = os.path.join(self.static_folder_logo, company.logo_url)
            delete_file(file_path)

        return self.company_repository.delete_company(company)
