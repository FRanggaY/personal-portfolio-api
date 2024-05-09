from fastapi import APIRouter
from .endpoints import auth, role, user
from .endpoints.company import company, company_translation
from .endpoints.school import school, school_translation
from .endpoints.skill import skill, skill_translation, skill_mapping
from .endpoints.education import education, education_translation
from .endpoints.experience import experience, experience_translation
from .endpoints.solution import solution, solution_translation
from .endpoints.project import project, project_translation, project_attachment, project_skill
from .endpoints.public_profile import public_profile, public_profile_education, public_profile_experience, public_profile_skill, public_profile_solution, public_profile_project

router = APIRouter()

router.include_router(public_profile.router, prefix="/public-profile", tags=["Public Profile"])
router.include_router(public_profile_education.router, prefix="/public-profile", tags=["Public Profile"])
router.include_router(public_profile_experience.router, prefix="/public-profile", tags=["Public Profile"])
router.include_router(public_profile_skill.router, prefix="/public-profile", tags=["Public Profile"])
router.include_router(public_profile_solution.router, prefix="/public-profile", tags=["Public Profile"])
router.include_router(public_profile_project.router, prefix="/public-profile", tags=["Public Profile"])

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

router.include_router(solution.router, prefix="/solution", tags=["Solution"])
router.include_router(solution_translation.router, prefix="/solution-translation", tags=["Solution"])

router.include_router(project.router, prefix="/project", tags=["Project"])
router.include_router(project_translation.router, prefix="/project-translation", tags=["Project"])
router.include_router(project_attachment.router, prefix="/project-attachment", tags=["Project"])
router.include_router(project_skill.router, prefix="/project-skill", tags=["Project"])