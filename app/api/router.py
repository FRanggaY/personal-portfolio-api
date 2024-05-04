from fastapi import APIRouter
from .endpoints import auth, role, user
from .endpoints.company import company, company_translation
from .endpoints.school import school, school_translation
from .endpoints.skill import skill, skill_translation, skill_mapping
from .endpoints.education import education, education_translation
from .endpoints.experience import experience, experience_translation

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["Auth"])

router.include_router(role.router, prefix="/role", tags=["User"])
router.include_router(user.router, prefix="/user", tags=["User"])

router.include_router(company.router, prefix="/company", tags=["Company"])
router.include_router(company_translation.router, prefix="/company-translation", tags=["Company"])

router.include_router(school.router, prefix="/school", tags=["School"])
router.include_router(school_translation.router, prefix="/school-translation", tags=["School"])

router.include_router(skill.router, prefix="/skill", tags=["Skill"])
router.include_router(skill_translation.router, prefix="/skill-translation", tags=["Skill"])
router.include_router(skill_mapping.router, prefix="/skill-mapping", tags=["Skill"])

router.include_router(education.router, prefix="/education", tags=["Education"])
router.include_router(education_translation.router, prefix="/education-translation", tags=["Education"])

router.include_router(experience.router, prefix="/experience", tags=["Experience"])
router.include_router(experience_translation.router, prefix="/experience-translation", tags=["Experience"])