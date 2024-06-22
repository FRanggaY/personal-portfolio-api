import uuid
from sqlalchemy import asc, desc, or_
from sqlalchemy.orm import Session
from app.models.role.role import Role
from app.models.user import User

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: User):
        user.is_active = 1
        user.id = str(uuid.uuid4())
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_user_by_username(self, username: str) -> User:
        return self.db.query(User).filter(User.username == username).first()
   
    def get_user_by_credential(self, username_or_email: str) -> User:
       return self.db.query(User).filter(or_(User.username.ilike(username_or_email), User.email.ilike(username_or_email))).first()

    def get_user_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()
    
    def read_users(
        self, 
        role_id: int = None, 
        sort_by: str = None, 
        sort_order: str = 'asc', 
        custom_filters: dict = None,
        offset: int = None, 
        size: int = None,
        is_role_level: bool = False,
        role_level: int = None,
        user_id: str = None,
        is_active: bool = None,
    ) -> list[User]:
        query = self.db.query(User)

        # Filtering
        if role_id is not None:
            query = query.filter(User.role_id == role_id)

        if is_role_level and role_level is not None:
            query = query.filter(User.role.has(Role.level >= role_level))
        
        if user_id is not None:
            query = query.filter(User.id == user_id)

        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(User, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(User, column) == value)

        # Sorting
        if sort_by is not None:
            if sort_order == 'asc' and hasattr(User, sort_by):
                query = query.order_by(asc(getattr(User, sort_by)))
            elif sort_order == 'desc' and hasattr(User, sort_by):
                query = query.order_by(desc(getattr(User, sort_by)))

        # Pagination
        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        return query.all()
    
    def count_users(
        self, 
        role_id: int = None, 
        custom_filters: dict = None,
        is_role_level: bool = False,
        role_level: int = None,
        is_active: bool = None,
        user_id: str = None,
    ) -> int:
        query = self.db.query(User)

        # Filtering
        if role_id is not None:
            query = query.filter(User.role_id == role_id)

        if is_role_level and role_level is not None:
            query = query.filter(User.role.has(Role.level >= role_level))

        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        if user_id is not None:
            query = query.filter(User.id == user_id)

        # Apply custom filters
        if custom_filters is not None:
            for column, value in custom_filters.items():
                if isinstance(value, str):
                    query = query.filter(getattr(User, column).like(f'%{value}%'))
                else:
                    query = query.filter(getattr(User, column) == value)

        return query.count()

    def update_user(self, user: User):
        self.db.commit()
        return user

    def read_user(self, id: str) -> User:
        user = self.db.query(User).filter(User.id == id).first()
        return user

    def delete_user(self, user: User) -> str:
        user_id = user.id
        self.db.delete(user)
        self.db.commit()
        return user_id
