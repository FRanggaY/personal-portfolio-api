from sqlalchemy.orm import relationship
from sqlalchemy import Column, Date, DateTime, Integer, String, func, ForeignKey, Boolean
from enum import Enum as EnumParam

from app.database import Base

class Solution(Base):
    __tablename__ = "solutions"
    id = Column(String, primary_key=True, nullable=False)
    user_id = Column(ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=True)
    title = Column(String(128), unique=False, nullable=False)
    image_url = Column(String(512), unique=False, nullable=True)
    logo_url = Column(String(512), unique=False, nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, server_default=func.NOW(), nullable=False)
    updated_at = Column(DateTime, server_default=func.NOW(), onupdate=func.NOW(), nullable=False)

    solution_translations = relationship('SolutionTranslation', back_populates='solution', cascade='all, delete')
    user = relationship('User', back_populates='solutions')