from fastapi import APIRouter, Depends, Form, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import LanguageOption
from app.models.response import GeneralDataResponse
from app.models.role.role_authority import RoleAuthorityFeature, RoleAuthorityName
from app.models.experience.experience_translation import ExperienceTranslation
from app.services.experience.experience_service import ExperienceService
from app.services.role.role_authority_service import RoleAuthorityService
from app.services.experience.experience_translation_service import ExperienceTranslationService
from app.services.user_service import UserService
from app.utils.authentication import Authentication

router = APIRouter()

@router.post("", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
async def create_experience_translation(
    experience_id: str = Form(..., min_length=1, max_length=36),
    language_id: LanguageOption = Form(...),
    title: str = Form(..., min_length=1, max_length=128),
    employee_type: str = Form(..., min_length=1, max_length=128),
    location: str = Form(..., min_length=1, max_length=128),
    location_type: str = Form(..., min_length=1, max_length=128),
    description: str = Form(None, min_length=0, max_length=512),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Create Experience Translation

        - should login
        - allow to create with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    experience_translation_service = ExperienceTranslationService(db)
    experience_service = ExperienceService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.experience.value, name=RoleAuthorityName.create.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to create")
    
    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.experience_other.value, name=RoleAuthorityName.create.value)
    if role_authority:
        user_id_filter = None

    language_id = language_id.value

    # validation
    exist_experience = experience_service.experience_repository.read_experience(experience_id)
    if not exist_experience:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
    
    if user_id_filter is not None and exist_experience.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to create")

    exist_data = experience_translation_service.experience_translation_repository.get_experience_translation_by_experience_id_and_language_id(experience_id=experience_id, language_id=language_id)
    if exist_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Experience Translation already exist")
    
    try:
        experience_translation_model = ExperienceTranslation(
            language_id=language_id,
            experience_id=experience_id,
            description=description,
            title=title,
            employee_type=employee_type,
            location=location,
            location_type=location_type,
        )

        data = experience_translation_service.experience_translation_repository.create_experience_translation(experience_translation_model)
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

@router.get("/{experience_id}/{language_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
def read_experience_translation(
    experience_id: str,
    language_id: LanguageOption,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read Experience Translation

        - should login
    """
    user_id_active = payload.get("uid", None)
    experience_translation_service = ExperienceTranslationService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)

    user_id_filter = user_id_active

    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.experience_other.value, name=RoleAuthorityName.view.value)
    if role_authority:
        user_id_filter = None

    experience_translation = experience_translation_service.experience_translation_repository.get_experience_translation_by_experience_id_and_language_id(experience_id=experience_id, language_id=language_id.value)

    if not experience_translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

    if user_id_filter is not None and experience_translation.experience.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to read")

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data={
            'id': experience_translation.id,
            'title': experience_translation.title,
            'employee_type': experience_translation.employee_type,
            'location': experience_translation.location,
            'location_type': experience_translation.location_type,
            'description': experience_translation.description,
            'language_id': experience_translation.language_id,
            'created_at': str(experience_translation.created_at),
            'updated_at': str(experience_translation.updated_at),
        },
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.patch("/{experience_id}/{language_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def update_experience_translation(
    experience_id: str,
    language_id: LanguageOption,
    title: str = Form(None, min_length=1, max_length=128),
    employee_type: str = Form(None, min_length=1, max_length=128),
    location: str = Form(None, min_length=1, max_length=128),
    location_type: str = Form(None, min_length=1, max_length=128),
    description: str = Form(None, min_length=0, max_length=512),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Update Experience Translation
        
        - should login
        - allow to update with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    experience_translation_service = ExperienceTranslationService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.experience.value, name=RoleAuthorityName.edit.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to edit")
    
    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.experience_other.value, name=RoleAuthorityName.edit.value)
    if role_authority:
        user_id_filter = None

    # validation
    exist_experience_translation = experience_translation_service.experience_translation_repository.get_experience_translation_by_experience_id_and_language_id(experience_id=experience_id, language_id=language_id.value)
    if not exist_experience_translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience Translation not found")
    
    if user_id_filter is not None and exist_experience_translation.experience.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update")

    try:
        experience_translation_model = ExperienceTranslation(
            id=exist_experience_translation.id,
            language_id=language_id.value,
            experience_id=experience_id,
            description=description,
            title=title,
            employee_type=employee_type,
            location=location,
            location_type=location_type,
        )

        data = experience_translation_service.update_experience_translation(
            exist_experience_translation,
            experience_translation_model,
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


@router.delete("/{experience_id}/{language_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def delete_experience_translation(
    experience_id: str,
    language_id: LanguageOption,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Delete ExperienceTranslation
        
        - should login
        - allow to delete with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    experience_translation_service = ExperienceTranslationService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.experience.value, name=RoleAuthorityName.delete.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to delete")

    exist_experience_translation = experience_translation_service.experience_translation_repository.get_experience_translation_by_experience_id_and_language_id(experience_id, language_id)
    if not exist_experience_translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")

    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.experience_other.value, name=RoleAuthorityName.delete.value)
    if role_authority:
        user_id_filter = None

    if user_id_filter is not None and exist_experience_translation.experience.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to delete")

    try:
        experience_translation_service.experience_translation_repository.delete_experience_translation(exist_experience_translation)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    status_code = status.HTTP_200_OK
    data = {
        'experience_id': experience_id,
        'language_id': language_id,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response