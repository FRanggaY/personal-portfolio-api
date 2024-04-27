from fastapi import APIRouter, Depends, Form, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import LanguageOption
from app.models.response import GeneralDataResponse
from app.models.role_authority import RoleAuthorityFeature, RoleAuthorityName
from app.models.school.school_translation import SchoolTranslation
from app.services.school.school_service import SchoolService
from app.services.role_authority_service import RoleAuthorityService
from app.services.school.school_translation_service import SchoolTranslationService
from app.services.user_service import UserService
from app.utils.authentication import Authentication

router = APIRouter()

@router.post("", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
async def create_school_translation(
    school_id: str = Form(..., min_length=1, max_length=36),
    language_id: LanguageOption = Form(...),
    name: str = Form(..., min_length=1, max_length=128),
    description: str = Form(None, min_length=0, max_length=512),
    address: str = Form(None, min_length=0, max_length=512),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Create School Translation

        - should login
        - allow to create with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    school_translation_service = SchoolTranslationService(db)
    school_service = SchoolService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.school.value, name=RoleAuthorityName.create.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to create")

    language_id = language_id.value

    # validation
    exist_school = school_service.school_repository.read_school(school_id)
    if not exist_school:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="School not found")
    
    exist_data = school_translation_service.school_translation_repository.get_school_translation_by_school_id_and_language_id(school_id=school_id, language_id=language_id)
    if exist_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="School Translation already exist")
    
    try:
        school_translation_model = SchoolTranslation(
            language_id=language_id,
            school_id=school_id,
            address=address,
            description=description,
            name=name,
        )

        data = school_translation_service.school_translation_repository.create_school_translation(school_translation_model)
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

@router.get("/{school_id}/{language_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
def read_school_translation(
    school_id: str,
    language_id: LanguageOption,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read School Translation

        - should login
    """
    school_translation_service = SchoolTranslationService(db)
    school_translation = school_translation_service.school_translation_repository.get_school_translation_by_school_id_and_language_id(school_id=school_id, language_id=language_id.value)

    if not school_translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data={
            'id': school_translation.id,
            'name': school_translation.name,
            'description': school_translation.description,
            'address': school_translation.address,
            'language_id': school_translation.language_id,
            'created_at': str(school_translation.created_at),
            'updated_at': str(school_translation.updated_at),
        },
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.patch("/{school_id}/{language_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def update_school_translation(
    school_id: str,
    language_id: LanguageOption,
    name: str = Form(..., min_length=1, max_length=128),
    description: str = Form(None, min_length=0, max_length=512),
    address: str = Form(None, min_length=0, max_length=512),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Update School Translation
        
        - should login
        - allow to update with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    school_translation_service = SchoolTranslationService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.school.value, name=RoleAuthorityName.edit.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to edit")
    
    # validation
    exist_school_translation = school_translation_service.school_translation_repository.get_school_translation_by_school_id_and_language_id(school_id=school_id, language_id=language_id.value)
    if not exist_school_translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="School Translation not found")
    
    try:
        school_translation_model = SchoolTranslation(
            id=exist_school_translation.id,
            language_id=language_id.value,
            school_id=school_id,
            code=description,
            email=address,
            name=name,
        )

        data = school_translation_service.update_school_translation(
            exist_school_translation,
            school_translation_model,
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


@router.delete("/{school_id}/{language_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def delete_school_translation(
    school_id: str,
    language_id: LanguageOption,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Delete SchoolTranslation
        
        - should login
        - allow to delete with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    school_translation_service = SchoolTranslationService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.school.value, name=RoleAuthorityName.delete.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to delete")

    try:
        school_translation_service.delete_school_translation(school_id=school_id, language_id=language_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    status_code = status.HTTP_200_OK
    data = {
        'school_id': school_id,
        'language_id': language_id,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response