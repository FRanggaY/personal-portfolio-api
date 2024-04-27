from sqlalchemy.orm import Session
from app.dtos.auth import AuthLogin
from app.repositories.auth_repository import AuthRepository
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = UserRepository(db)
        self.auth_repository = AuthRepository(db)

    def auth_login(self, auth_login: AuthLogin):
        user = self.user_repository.get_user_by_credential(auth_login.username_or_email)
        if not user:
            raise ValueError('Credential failed')
        
        if not user.is_active:
            raise ValueError('User is not active')
        
        user_service = UserService(self.db)
        is_password_valid = user_service.verify_password(auth_login.password, user.password)
        return self.auth_repository.auth_login(user, is_password_valid)