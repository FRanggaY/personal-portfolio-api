import os
import uuid
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.utils.handling_file import delete_file, upload_file

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.static_folder_image = "static/images/user"
    
    def verify_password(self, plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return pwd_context.hash(password)
    
    def create_user(self, user: User, image: UploadFile = None, file_extension = None):
        user.image_url = upload_file(image, self.static_folder_image, file_extension, user.username) if image else ''

        return self.user_repository.create_user(user)
    
    def validation_unique_based_other_user(self, exist_user: User, user: User):
        if user.username:
            exist_username = self.user_repository.get_user_by_username(user.username)
            if exist_username and (exist_user.id != exist_username.id):
                raise ValueError('Username already used in other account')
            exist_user.username = user.username
        
        if user.email:
            exist_email = self.user_repository.get_user_by_email(user.email)
            if exist_email and (exist_user.id != exist_email.id):
                raise ValueError('Email already used in other account')
            exist_user.email = user.email

    def update_user(self, exist_user: User, user: User, image: UploadFile = None, file_extension = None):
        self.validation_unique_based_other_user(exist_user, user)
        
        if user.name:
            exist_user.name = user.name
        
        exist_user.no_handphone = user.no_handphone    
        exist_user.role_id = user.role_id
        exist_user.is_active = user.is_active
        exist_user.gender = user.gender

        if image and exist_user.image_url:
            file_path = os.path.join(self.static_folder_image, exist_user.image_url)
            delete_file(file_path)
            exist_user.image_url = upload_file(image, self.static_folder_image, file_extension, user.username)

        if image and not exist_user.image_url:
            exist_user.image_url = upload_file(image, self.static_folder_image, file_extension, user.username)

        return self.user_repository.update_user(exist_user)
    
    def update_user_password(self, exist_user: User, user: User):
        if user.password:
            exist_user.password = user.password

        return self.user_repository.update_user(exist_user)
    
    def delete_user(self, user_id: str):
        user = self.user_repository.read_user(user_id)
        if not user:
            raise ValueError("User not found")

        if user.image_url:
            file_path = os.path.join(self.static_folder_image, user.image_url)
            delete_file(file_path)

        return self.user_repository.delete_user(user)
