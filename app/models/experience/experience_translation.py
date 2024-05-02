from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, String, func, ForeignKey, Boolean, Enum
from enum import Enum as EnumParam

from app.database import Base
from app.models.experience import experience

class ExperienceTranslation(Base):
    __tablename__ = "experience_translations"

    id = Column(String, primary_key=True, index=True)
    experience_id = Column(ForeignKey('experiences.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    title = Column(String(128), unique=False, nullable=False)
    description = Column(String(512), unique=False, nullable=True)
    employee_type = Column(String(128), unique=False, nullable=False)
    location = Column(String(128), unique=False, nullable=False)
    location_type = Column(String(128), unique=False, nullable=False)
    language_id = Column(Enum('id', 'en'), nullable=True)
    created_at = Column(DateTime, server_default=func.NOW(), nullable=False)
    updated_at = Column(DateTime, server_default=func.NOW(), onupdate=func.NOW(), nullable=False)
    
    experience = relationship('Experience', back_populates='experience_translations')