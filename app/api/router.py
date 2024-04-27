from fastapi import APIRouter
from .endpoints import auth, role, user

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Auth"])

router.include_router(role.router, prefix="/role", tags=["User"])
router.include_router(user.router, prefix="/user", tags=["User"])