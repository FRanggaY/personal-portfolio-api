from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, String, func, ForeignKey, Boolean, Enum
from enum import Enum as EnumParam

from app.database import Base
from app.models.education import education

class EducationTranslation(Base):
    __tablename__ = "education_translations"

    id = Column(String, primary_key=True, index=True)
    education_id = Column(ForeignKey('educations.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    title = Column(String(128), unique=False, nullable=False)
    degree = Column(String(128), unique=False, nullable=False)
    field_of_study = Column(String(128), unique=False, nullable=False)
    description = Column(String(512), unique=False, nullable=True)
    language_id = Column(Enum('id', 'en'), nullable=True)
    created_at = Column(DateTime, server_default=func.NOW(), nullable=False)
    updated_at = Column(DateTime, server_default=func.NOW(), onupdate=func.NOW(), nullable=False)
    
    education = relationship('Education', back_populates='education_translations')