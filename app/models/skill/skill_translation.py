from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, String, func, ForeignKey, Boolean, Enum
from enum import Enum as EnumParam

from app.database import Base
from app.models.skill import skill

class SkillTranslation(Base):
    __tablename__ = "skill_translations"

    id = Column(String, primary_key=True, index=True)
    skill_id = Column(ForeignKey('skills.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    name = Column(String(128), unique=False, nullable=False)
    description = Column(String(512), unique=False, nullable=True)
    language_id = Column(Enum('id', 'en'), nullable=True)
    created_at = Column(DateTime, server_default=func.NOW(), nullable=False)
    updated_at = Column(DateTime, server_default=func.NOW(), onupdate=func.NOW(), nullable=False)
    
    skill = relationship('Skill', back_populates='skill_translations')