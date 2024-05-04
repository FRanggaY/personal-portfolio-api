from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, String, func, ForeignKey, Boolean, Enum
from enum import Enum as EnumParam

from app.database import Base
from app.models.skill import skill

class SkillMapping(Base):
    __tablename__ = "skill_mappings"
    id = Column(String, primary_key=True, nullable=False)
    skill_id = Column(ForeignKey('skills.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.NOW(), nullable=False)
    updated_at = Column(DateTime, server_default=func.NOW(), onupdate=func.NOW(), nullable=False)

    skill = relationship('Skill', back_populates='skill_mappings')
    user = relationship('User', back_populates='skill_mappings')