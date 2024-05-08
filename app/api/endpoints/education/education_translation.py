from fastapi import APIRouter, Depends, Form, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import LanguageOption
from app.models.response import GeneralDataResponse
from app.models.role_authority import RoleAuthorityFeature, RoleAuthorityName
from app.models.education.education_translation import EducationTranslation
from app.services.education.education_service import EducationService
from app.services.role_authority_service import RoleAuthorityService
from app.services.education.education_translation_service import EducationTranslationService
from app.services.user_service import UserService
from app.utils.authentication import Authentication

router = APIRouter()

@router.post("", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
async def create_education_translation(
    education_id: str = Form(..., min_length=1, max_length=36),
    language_id: LanguageOption = Form(...),
    title: str = Form(..., min_length=1, max_length=128),
    degree: str = Form(..., min_length=1, max_length=128),
    field_of_study: str = Form(..., min_length=1, max_length=128),
    description: str = Form(None, min_length=0, max_length=512),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Create Education Translation

        - should login
        - allow to create with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    education_translation_service = EducationTranslationService(db)
    education_service = EducationService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.education.value, name=RoleAuthorityName.create.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to create")

    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.education_other.value, name=RoleAuthorityName.create.value)
    if role_authority:
        user_id_filter = None

    language_id = language_id.value

    # validation
    exist_education = education_service.education_repository.read_education(education_id)
    if not exist_education:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education not found")
    
    if user_id_filter is not None and exist_education.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to create")

    exist_data = education_translation_service.education_translation_repository.get_education_translation_by_education_id_and_language_id(education_id=education_id, language_id=language_id)
    if exist_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Education Translation already exist")
    
    try:
        education_translation_model = EducationTranslation(
            language_id=language_id,
            education_id=education_id,
            description=description,
            title=title,
            degree=degree,
            field_of_study=field_of_study,
        )

        data = education_translation_service.education_translation_repository.create_education_translation(education_translation_model)
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

@router.get("/{education_id}/{language_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
def read_education_translation(
    education_id: str,
    language_id: LanguageOption,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read Education Translation

        - should login
    """
    user_id_active = payload.get("uid", None)
    education_translation_service = EducationTranslationService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)

    user_id_filter = user_id_active
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.education_other.value, name=RoleAuthorityName.view.value)
    if role_authority:
        user_id_filter = None

    education_translation = education_translation_service.education_translation_repository.get_education_translation_by_education_id_and_language_id(education_id=education_id, language_id=language_id.value)

    if not education_translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")
    
    if user_id_filter is not None and education_translation.education.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to read")

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data={
            'id': education_translation.id,
            'title': education_translation.title,
            'degree': education_translation.degree,
            'field_of_study': education_translation.field_of_study,
            'description': education_translation.description,
            'language_id': education_translation.language_id,
            'created_at': str(education_translation.created_at),
            'updated_at': str(education_translation.updated_at),
        },
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.patch("/{education_id}/{language_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def update_education_translation(
    education_id: str,
    language_id: LanguageOption,
    title: str = Form(None, min_length=1, max_length=128),
    degree: str = Form(None, min_length=1, max_length=128),
    field_of_study: str = Form(None, min_length=1, max_length=128),
    description: str = Form(None, min_length=0, max_length=512),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Update Education Translation
        
        - should login
        - allow to update with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    education_translation_service = EducationTranslationService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.education.value, name=RoleAuthorityName.edit.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to edit")
    
    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.education_other.value, name=RoleAuthorityName.edit.value)
    if role_authority:
        user_id_filter = None

    # validation
    exist_education_translation = education_translation_service.education_translation_repository.get_education_translation_by_education_id_and_language_id(education_id=education_id, language_id=language_id.value)
    if not exist_education_translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education Translation not found")
    
      
    if user_id_filter is not None and exist_education_translation.education.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update")

    try:
        education_translation_model = EducationTranslation(
            id=exist_education_translation.id,
            language_id=language_id.value,
            education_id=education_id,
            description=description,
            title=title,
            degree=degree,
            field_of_study=field_of_study,
        )

        data = education_translation_service.update_education_translation(
            exist_education_translation,
            education_translation_model,
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


@router.delete("/{education_id}/{language_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def delete_education_translation(
    education_id: str,
    language_id: LanguageOption,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Delete EducationTranslation
        
        - should login
        - allow to delete with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    education_translation_service = EducationTranslationService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.education.value, name=RoleAuthorityName.delete.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to delete")

    exist_education_translation = education_translation_service.education_translation_repository.get_education_translation_by_education_id_and_language_id(education_id, language_id)
    if not exist_education_translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education not found")

    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.education_other.value, name=RoleAuthorityName.delete.value)
    if role_authority:
        user_id_filter = None

    if user_id_filter is not None and exist_education_translation.education.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to delete")

    try:
        education_translation_service.education_translation_repository.delete_education_translation(exist_education_translation)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    status_code = status.HTTP_200_OK
    data = {
        'education_id': education_id,
        'language_id': language_id,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response