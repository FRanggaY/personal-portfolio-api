from fastapi import APIRouter
from .endpoints import auth, role, user
from .endpoints.company import company, company_translation

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Auth"])

router.include_router(role.router, prefix="/role", tags=["User"])
router.include_router(user.router, prefix="/user", tags=["User"])

router.include_router(company.router, prefix="/company", tags=["Company"])
router.include_router(company_translation.router, prefix="/company-translation", tags=["Company"])