import uuid
from sqlalchemy import asc, desc
from sqlalchemy.orm import Session
from app.models.role_authority import RoleAuthority

class RoleAuthorityRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_role_authority(self, role_authority: RoleAuthority):
        role_authority.id = str(uuid.uuid4())
        self.db.add(role_authority)
        self.db.commit()
        self.db.refresh(role_authority)
        return role_authority
    
    def get_role_authority_by_specific(self, role_id: int, name: str, feature: str) -> RoleAuthority:
        return self.db.query(RoleAuthority).filter(RoleAuthority.role_id == role_id,  RoleAuthority.name == name, RoleAuthority.feature == feature).first()

    def read_role_authorities(
        self, 
        offset: int = None, 
        size: int = None,
        role_id: int = None,
        feature: str | list = None,
        name: str = None,
        sort_by: str = None, 
        sort_order: str = 'asc', 
    ) -> list[RoleAuthority]:
        query = self.db.query(RoleAuthority)

        if role_id is not None:
            query = query.filter(RoleAuthority.role_id == role_id)

        if feature is not None:
            if(isinstance(feature, list)):
                query = query.filter(RoleAuthority.feature.in_(feature))
            else:
                query = query.filter(RoleAuthority.feature == feature)
        
        if name is not None:
            query = query.filter(RoleAuthority.name == name)

        # Sorting
        if sort_by is not None:
            if sort_order == 'asc' and hasattr(RoleAuthority, sort_by):
                query = query.order_by(asc(getattr(RoleAuthority, sort_by)))
            elif sort_order == 'desc' and hasattr(RoleAuthority, sort_by):
                query = query.order_by(desc(getattr(RoleAuthority, sort_by)))
        else:
            query = query.order_by(asc(RoleAuthority.feature))

        # Pagination
        if offset is not None and size is not None:
            query = query.offset((offset - 1) * size).limit(size)

        return query.all()
    
    def count_role_authorities(
        self,
        role_id: int = None,
        feature: str = None,
        name: str = None,
    ) -> int:
        query = self.db.query(RoleAuthority)

        if role_id is not None:
            query = query.filter(RoleAuthority.role_id == role_id)

        if feature is not None:
            query = query.filter(RoleAuthority.feature == feature)
        
        if name is not None:
            query = query.filter(RoleAuthority.name == name)

        return query.count()

    def read_role_authority(self, id: str) -> RoleAuthority:
        role_authority = self.db.query(RoleAuthority).filter(RoleAuthority.id == id).first()
        return role_authority

    def delete_role_authority(self, role_authority: RoleAuthority) -> int:
        role_authority_id = role_authority.id
        self.db.delete(role_authority)
        self.db.commit()
        return role_authority_id
