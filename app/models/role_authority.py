from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, String, func, ForeignKey, Boolean, Enum
from enum import Enum as EnumParam

from app.database import Base

class RoleAuthority(Base):
    __tablename__ = "role_authorities"

    id = Column(String, primary_key=True, index=True)
    role_id = Column(ForeignKey('roles.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    name = Column(String(36), unique=False, nullable=False)
    feature = Column(String(36), unique=False, nullable=False)
    description = Column(String(256), unique=False, nullable=True)
    created_at = Column(DateTime, server_default=func.NOW(), nullable=False)
    updated_at = Column(DateTime, server_default=func.NOW(), onupdate=func.NOW(), nullable=False)
    
    role = relationship('Role', back_populates='role_authorities')

class RoleAuthorityName(EnumParam):
    view = "view"
    create = "create"
    edit = "edit"
    delete = "delete"
    assign = "assign"
    unassign = "unassign"

class RoleAuthorityFeature(EnumParam):
    role = "role"
    user = "user"
    school = "school"
    company = "company"
    education = "education"
    experience = "experience"
    skill = "skill"
    service = "service"
    project = "project"