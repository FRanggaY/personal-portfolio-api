from sqlalchemy.orm import relationship
from sqlalchemy import Column, DateTime, Integer, String, func, ForeignKey, Boolean
from enum import Enum as EnumParam

from app.database import Base

class Company(Base):
    __tablename__ = "companies"
    id = Column(String, primary_key=True, nullable=False)
    code = Column(String(36), unique=True, nullable=False)
    name = Column(String(128), unique=True, nullable=False)
    image_url = Column(String(512), unique=False, nullable=True)
    logo_url = Column(String(512), unique=False, nullable=True)
    website_url = Column(String(512), unique=False, nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.NOW(), nullable=False)
    updated_at = Column(DateTime, server_default=func.NOW(), onupdate=func.NOW(), nullable=False)

    company_translations = relationship('CompanyTranslation', back_populates='company', cascade='all, delete')
    experiences = relationship('Experience', back_populates='company', cascade='all, delete')
    