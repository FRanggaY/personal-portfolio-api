from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, String, func, ForeignKey, Boolean, Enum
from enum import Enum as EnumParam

from app.database import Base
from app.models import role

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    role_id = Column(ForeignKey('roles.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    username = Column(String(36), unique=True, nullable=False)
    email = Column(String(256),  unique=True, nullable=False)
    name = Column(String(36), unique=False, nullable=True)
    password = Column(String(512), unique=False, nullable=False)
    image_url = Column(String(512), unique=False, nullable=True)
    no_handphone = Column(String(256), unique=False, nullable=True)
    gender = Column(Enum('male', 'female'), nullable=True)
    is_active = Column(Boolean)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.NOW(), nullable=False)
    updated_at = Column(DateTime, server_default=func.NOW(), onupdate=func.NOW(), nullable=False)
    
    role = relationship('Role', back_populates='users')
    educations = relationship('Education', back_populates='user', cascade='all, delete')
    experiences = relationship('Experience', back_populates='user', cascade='all, delete')
    skill_mappings = relationship('SkillMapping', back_populates='user', cascade='all, delete')
    
class UserGender(EnumParam):
    male = "male"
    female = "female"