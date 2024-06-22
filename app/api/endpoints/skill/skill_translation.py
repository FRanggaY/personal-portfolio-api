from fastapi import APIRouter, Depends, Form, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import LanguageOption
from app.models.response import GeneralDataResponse
from app.models.role.role_authority import RoleAuthorityFeature, RoleAuthorityName
from app.models.skill.skill_translation import SkillTranslation
from app.services.skill.skill_service import SkillService
from app.services.role.role_authority_service import RoleAuthorityService
from app.services.skill.skill_translation_service import SkillTranslationService
from app.services.user_service import UserService
from app.utils.authentication import Authentication

router = APIRouter()

@router.post("", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
async def create_skill_translation(
    skill_id: str = Form(..., min_length=1, max_length=36),
    language_id: LanguageOption = Form(...),
    name: str = Form(..., min_length=1, max_length=128),
    description: str = Form(None, min_length=0, max_length=512),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Create Skill Translation

        - should login
        - allow to create with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    skill_translation_service = SkillTranslationService(db)
    skill_service = SkillService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.skill.value, name=RoleAuthorityName.create.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to create")

    language_id = language_id.value

    # validation
    exist_skill = skill_service.skill_repository.read_skill(skill_id)
    if not exist_skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    
    exist_data = skill_translation_service.skill_translation_repository.get_skill_translation_by_skill_id_and_language_id(skill_id=skill_id, language_id=language_id)
    if exist_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Skill Translation already exist")
    
    try:
        skill_translation_model = SkillTranslation(
            language_id=language_id,
            skill_id=skill_id,
            description=description,
            name=name,
        )

        data = skill_translation_service.skill_translation_repository.create_skill_translation(skill_translation_model)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    
    status_code = status.HTTP_201_CREATED
    result = {
        'id': data.id,
    }


    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=result,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.get("/{skill_id}/{language_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
def read_skill_translation(
    skill_id: str,
    language_id: LanguageOption,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read Skill Translation

        - should login
    """
    skill_translation_service = SkillTranslationService(db)
    skill_translation = skill_translation_service.skill_translation_repository.get_skill_translation_by_skill_id_and_language_id(skill_id=skill_id, language_id=language_id.value)

    if not skill_translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data={
            'id': skill_translation.id,
            'name': skill_translation.name,
            'description': skill_translation.description,
            'language_id': skill_translation.language_id,
            'created_at': str(skill_translation.created_at),
            'updated_at': str(skill_translation.updated_at),
        },
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.patch("/{skill_id}/{language_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def update_skill_translation(
    skill_id: str,
    language_id: LanguageOption,
    name: str = Form(..., min_length=1, max_length=128),
    description: str = Form(None, min_length=0, max_length=512),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Update Skill Translation
        
        - should login
        - allow to update with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    skill_translation_service = SkillTranslationService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.skill.value, name=RoleAuthorityName.edit.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to edit")
    
    # validation
    exist_skill_translation = skill_translation_service.skill_translation_repository.get_skill_translation_by_skill_id_and_language_id(skill_id=skill_id, language_id=language_id.value)
    if not exist_skill_translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill Translation not found")
    
    try:
        skill_translation_model = SkillTranslation(
            id=exist_skill_translation.id,
            language_id=language_id.value,
            skill_id=skill_id,
            description=description,
            name=name,
        )

        data = skill_translation_service.update_skill_translation(
            exist_skill_translation,
            skill_translation_model,
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    status_code = status.HTTP_200_OK
    data = {
        'id': data.id,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response


@router.delete("/{skill_id}/{language_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def delete_skill_translation(
    skill_id: str,
    language_id: LanguageOption,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Delete SkillTranslation
        
        - should login
        - allow to delete with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    skill_translation_service = SkillTranslationService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.skill.value, name=RoleAuthorityName.delete.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to delete")

    try:
        skill_translation_service.delete_skill_translation(skill_id=skill_id, language_id=language_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    status_code = status.HTTP_200_OK
    data = {
        'skill_id': skill_id,
        'language_id': language_id,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response