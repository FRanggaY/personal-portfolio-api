from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, String, func, ForeignKey, Boolean, Enum
from enum import Enum as EnumParam

from app.database import Base
from app.models.project import project
from app.models.skill import skill

class ProjectSkill(Base):
    __tablename__ = "project_skills"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(ForeignKey('projects.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    skill_id = Column(ForeignKey('skills.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.NOW(), nullable=False)
    updated_at = Column(DateTime, server_default=func.NOW(), onupdate=func.NOW(), nullable=False)
    
    project = relationship('Project', back_populates='project_skills')
    skill = relationship('Skill', back_populates='project_skills')