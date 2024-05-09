from sqlalchemy.orm import relationship
from sqlalchemy import Column, Date, DateTime, Integer, String, func, ForeignKey, Boolean
from enum import Enum as EnumParam

from app.database import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(String, primary_key=True, nullable=False)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    title = Column(String(128), unique=False, nullable=False)
    slug = Column(String(256), unique=False, nullable=False)
    image_url = Column(String(512), unique=False, nullable=True)
    logo_url = Column(String(512), unique=False, nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.NOW(), nullable=False)
    updated_at = Column(DateTime, server_default=func.NOW(), onupdate=func.NOW(), nullable=False)

    project_translations = relationship('ProjectTranslation', back_populates='project', cascade='all, delete')
    project_attachments = relationship('ProjectAttachment', back_populates='project', cascade='all, delete')
    project_skills = relationship('ProjectSkill', back_populates='project', cascade='all, delete')
    user = relationship('User', back_populates='projects')