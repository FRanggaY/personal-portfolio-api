from typing import Optional
from pydantic import BaseModel, Field

class AuthLogin(BaseModel):
    username_or_email: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=1, max_length=512)

class AuthProfilePassword(BaseModel):
    old_password: str = Field(..., min_length=1, max_length=512)
    new_password: str = Field(..., min_length=1, max_length=512)
    confirm_new_password: str = Field(..., min_length=1, max_length=512)
