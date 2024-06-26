from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, String, func, ForeignKey, Boolean, Enum
from enum import Enum as EnumParam

from app.database import Base
from app.models.school import school

class SchoolTranslation(Base):
    __tablename__ = "school_translations"

    id = Column(String, primary_key=True, index=True)
    school_id = Column(ForeignKey('schools.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    name = Column(String(128), unique=False, nullable=False)
    description = Column(String(512), unique=False, nullable=True)
    address = Column(String(512), unique=False, nullable=True)
    language_id = Column(Enum('id', 'en'), nullable=True)
    created_at = Column(DateTime, server_default=func.NOW(), nullable=False)
    updated_at = Column(DateTime, server_default=func.NOW(), onupdate=func.NOW(), nullable=False)
    
    school = relationship('School', back_populates='school_translations')