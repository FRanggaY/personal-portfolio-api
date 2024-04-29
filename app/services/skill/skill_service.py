import os
import uuid
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.skill.skill import Skill
from app.repositories.skill.skill_repository import SkillRepository
from app.utils.handling_file import delete_file, upload_file

class SkillService:
    def __init__(self, db: Session):
        self.db = db
        self.skill_repository = SkillRepository(db)
        self.static_folder_image = "static/images/skill/image"
        self.static_folder_logo = "static/images/skill/logo"
    
    def create_skill(self, skill: Skill, image: UploadFile = None, logo: UploadFile = None, file_extension = None):
        skill.image_url = upload_file(image, self.static_folder_image, file_extension, skill.code) if image else ''
        skill.logo_url = upload_file(logo, self.static_folder_logo, file_extension, skill.code) if logo else ''

        return self.skill_repository.create_skill(skill)
    
    def validation_unique_based_other_skill(self, exist_skill: Skill, skill: Skill):
        if skill.code:
            exist_code = self.skill_repository.get_skill_by_code(skill.code)
            if exist_code and (exist_skill.id != exist_code.id):
                raise ValueError('Code already used in other account')
            exist_skill.code = skill.code
        
        if skill.name:
            exist_name = self.skill_repository.get_skill_by_name(skill.name)
            if exist_name and (exist_skill.id != exist_name.id):
                raise ValueError('Name already used in other account')
            exist_skill.name = skill.name

    def update_skill(
        self, 
        exist_skill: Skill, 
        skill: Skill, 
        image: UploadFile = None,
        logo: UploadFile = None,
        file_extension = None
    ):
        self.validation_unique_based_other_skill(exist_skill, skill)
        
        exist_skill.website_url = skill.website_url
        exist_skill.category = skill.category
        exist_skill.is_active = skill.is_active
        exist_skill.created_at = skill.category

        if image and not exist_skill.image_url:
            exist_skill.image_url = upload_file(image, self.static_folder_image, file_extension, skill.code)

        if image and exist_skill.image_url:
            file_path = os.path.join(self.static_folder_image, exist_skill.image_url)
            delete_file(file_path)
            exist_skill.image_url = upload_file(image, self.static_folder_image, file_extension, skill.code)
        
        if logo and not exist_skill.logo_url:
            exist_skill.logo_url = upload_file(logo, self.static_folder_logo, file_extension, skill.code)

        if logo and exist_skill.logo_url:
            file_path = os.path.join(self.static_folder_logo, exist_skill.logo_url)
            delete_file(file_path)
            exist_skill.logo_url = upload_file(logo, self.static_folder_logo, file_extension, skill.code)

        return self.skill_repository.update_skill(exist_skill)
    
    def delete_skill(self, skill_id: str):
        skill = self.skill_repository.read_skill(skill_id)
        if not skill:
            raise ValueError("Skill not found")

        if skill.image_url:
            file_path = os.path.join(self.static_folder_image, skill.image_url)
            delete_file(file_path)

        return self.skill_repository.delete_skill(skill)
