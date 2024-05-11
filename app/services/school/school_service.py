import os
import uuid
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.school.school import School
from app.repositories.school.school_repository import SchoolRepository
from app.utils.handling_file import delete_file, upload_file

class SchoolService:
    def __init__(self, db: Session):
        self.db = db
        self.school_repository = SchoolRepository(db)
        self.static_folder_image = "static/images/school/image"
        self.static_folder_logo = "static/images/school/logo"
    
    def create_school(self, school: School, image: UploadFile = None, logo: UploadFile = None, file_extension_image = None, file_extension_logo = None):
        school.image_url = upload_file(image, self.static_folder_image, file_extension_image, school.code) if image else ''
        school.logo_url = upload_file(logo, self.static_folder_logo, file_extension_logo, school.code) if logo else ''

        return self.school_repository.create_school(school)
    
    def validation_unique_based_other_school(self, exist_school: School, school: School):
        if school.code:
            exist_code = self.school_repository.get_school_by_code(school.code)
            if exist_code and (exist_school.id != exist_code.id):
                raise ValueError('Code already used in other account')
            exist_school.code = school.code
        
        if school.name:
            exist_name = self.school_repository.get_school_by_name(school.name)
            if exist_name and (exist_school.id != exist_name.id):
                raise ValueError('Name already used in other account')
            exist_school.name = school.name

    def update_school(
        self, 
        exist_school: School, 
        school: School, 
        image: UploadFile = None,
        logo: UploadFile = None,
        file_extension_image = None,
        file_extension_logo = None,
    ):
        self.validation_unique_based_other_school(exist_school, school)
        
        exist_school.website_url = school.website_url
        exist_school.is_active = school.is_active

        if image and exist_school.image_url:
            file_path = os.path.join(self.static_folder_image, exist_school.image_url)
            delete_file(file_path)
            exist_school.image_url = upload_file(image, self.static_folder_image, file_extension_image, school.code)

        if image and not exist_school.image_url:
            exist_school.image_url = upload_file(image, self.static_folder_image, file_extension_image, school.code)

        if logo and exist_school.logo_url:
            file_path = os.path.join(self.static_folder_logo, exist_school.logo_url)
            delete_file(file_path)
            exist_school.logo_url = upload_file(logo, self.static_folder_logo, file_extension_logo, school.code)

        if logo and not exist_school.logo_url:
            exist_school.logo_url = upload_file(logo, self.static_folder_logo, file_extension_logo, school.code)

        return self.school_repository.update_school(exist_school)
    
    def delete_school(self, school_id: str):
        school = self.school_repository.read_school(school_id)
        if not school:
            raise ValueError("School not found")

        if school.image_url:
            file_path = os.path.join(self.static_folder_image, school.image_url)
            delete_file(file_path)

        if school.logo_url:
            file_path = os.path.join(self.static_folder_logo, school.logo_url)
            delete_file(file_path)

        return self.school_repository.delete_school(school)
