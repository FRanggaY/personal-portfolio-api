from sqlalchemy.orm import Session

from app.repositories.role_authority_repository import RoleAuthorityRepository

class RoleAuthorityService:
    def __init__(self, db: Session):
        self.db = db
        self.role_authority_repository = RoleAuthorityRepository(db)