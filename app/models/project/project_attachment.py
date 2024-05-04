from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, String, func, ForeignKey, Boolean, Enum
from enum import Enum as EnumParam

from app.database import Base
from app.models.project import project

class ProjectAttachment(Base):
    __tablename__ = "project_attachments"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(ForeignKey('projects.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    title = Column(String(128), unique=False, nullable=False)
    image_url = Column(String(512), unique=False, nullable=True)
    description = Column(String(512), unique=False, nullable=True)
    category = Column(String(512), unique=False, nullable=True)
    website_url = Column(String(512), unique=False, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.NOW(), nullable=False)
    updated_at = Column(DateTime, server_default=func.NOW(), onupdate=func.NOW(), nullable=False)
    
    project = relationship('Project', back_populates='project_attachments')