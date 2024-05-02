from sqlalchemy.orm import relationship
from sqlalchemy import Column, Date, DateTime, Integer, String, func, ForeignKey, Boolean
from enum import Enum as EnumParam

from app.database import Base

class Experience(Base):
    __tablename__ = "experiences"
    id = Column(String, primary_key=True, nullable=False)
    company_id = Column(ForeignKey('companies.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    title = Column(String(128), unique=False, nullable=False)
    started_at = Column(Date, nullable=True)
    finished_at = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.NOW(), nullable=False)
    updated_at = Column(DateTime, server_default=func.NOW(), onupdate=func.NOW(), nullable=False)

    experience_translations = relationship('ExperienceTranslation', back_populates='experience', cascade='all, delete')
    company = relationship('Company', back_populates='experiences')
    user = relationship('User', back_populates='experiences')