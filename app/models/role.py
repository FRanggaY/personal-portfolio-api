from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, Integer, String, func, ForeignKey, Boolean
from enum import Enum as EnumParam

from app.database import Base
from app.models import role_authority

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, nullable=False)
    code = Column(String(36), unique=True, nullable=False)
    level = Column(Integer, nullable=False, default=0)
    name = Column(String(126), unique=True, nullable=False)
    description = Column(String(256), unique=False, nullable=True)
    is_active = Column(Boolean)

    users = relationship('User', back_populates='role', cascade='all, delete')
    role_authorities = relationship('RoleAuthority', back_populates='role', cascade='all, delete')
    