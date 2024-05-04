from fastapi import APIRouter, Depends, Form, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import LanguageOption
from app.models.response import GeneralDataResponse
from app.models.role_authority import RoleAuthorityFeature, RoleAuthorityName
from app.models.project.project_translation import ProjectTranslation
from app.services.project.project_service import ProjectService
from app.services.role_authority_service import RoleAuthorityService
from app.services.project.project_translation_service import ProjectTranslationService
from app.services.user_service import UserService
from app.utils.authentication import Authentication

router = APIRouter()

@router.post("", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
async def create_project_translation(
    project_id: str = Form(..., min_length=1, max_length=36),
    language_id: LanguageOption = Form(...),
    title: str = Form(..., min_length=1, max_length=128),
    description: str = Form(None, min_length=0, max_length=512),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Create Project Translation

        - should login
        - allow to create with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    project_translation_service = ProjectTranslationService(db)
    project_service = ProjectService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.project.value, name=RoleAuthorityName.create.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to create")

    language_id = language_id.value

    # validation
    exist_project = project_service.project_repository.read_project(project_id)
    if not exist_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    exist_data = project_translation_service.project_translation_repository.get_project_translation_by_project_id_and_language_id(project_id=project_id, language_id=language_id)
    if exist_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project Translation already exist")
    
    try:
        project_translation_model = ProjectTranslation(
            language_id=language_id,
            project_id=project_id,
            description=description,
            title=title,
        )

        data = project_translation_service.project_translation_repository.create_project_translation(project_translation_model)
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

@router.get("/{project_id}/{language_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
def read_project_translation(
    project_id: str,
    language_id: LanguageOption,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read Project Translation

        - should login
    """
    user_id_active = payload.get("uid", None)
    project_translation_service = ProjectTranslationService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)

    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.project_other.value, name=RoleAuthorityName.view.value)
    if role_authority:
        user_id_filter = None

    project_translation = project_translation_service.project_translation_repository.get_project_translation_by_project_id_and_language_id(project_id=project_id, language_id=language_id.value)

    if not project_translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

    if not user_id_filter and project_translation.project.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to read")

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data={
            'id': project_translation.id,
            'title': project_translation.title,
            'description': project_translation.description,
            'language_id': project_translation.language_id,
            'created_at': str(project_translation.created_at),
            'updated_at': str(project_translation.updated_at),
        },
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.patch("/{project_id}/{language_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def update_project_translation(
    project_id: str,
    language_id: LanguageOption,
    title: str = Form(None, min_length=1, max_length=128),
    description: str = Form(None, min_length=0, max_length=512),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Update Project Translation
        
        - should login
        - allow to update with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    project_translation_service = ProjectTranslationService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.project.value, name=RoleAuthorityName.edit.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to edit")
    
    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.project_other.value, name=RoleAuthorityName.edit.value)
    if role_authority:
        user_id_filter = None

    # validation
    exist_project_translation = project_translation_service.project_translation_repository.get_project_translation_by_project_id_and_language_id(project_id=project_id, language_id=language_id.value)
    if not exist_project_translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project Translation not found")
    
    if not user_id_filter and exist_project_translation.project.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update")

    try:
        project_translation_model = ProjectTranslation(
            id=exist_project_translation.id,
            language_id=language_id.value,
            project_id=project_id,
            code=description,
            title=title,
        )

        data = project_translation_service.update_project_translation(
            exist_project_translation,
            project_translation_model,
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


@router.delete("/{project_id}/{language_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def delete_project_translation(
    project_id: str,
    language_id: LanguageOption,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Delete ProjectTranslation
        
        - should login
        - allow to delete with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    project_translation_service = ProjectTranslationService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.project.value, name=RoleAuthorityName.delete.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to delete")

    exist_project_translation = project_translation_service.project_translation_repository.get_project_translation_by_project_id_and_language_id(project_id, language_id)
    if not exist_project_translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.project_other.value, name=RoleAuthorityName.delete.value)
    if role_authority:
        user_id_filter = None

    if not user_id_filter and exist_project_translation.project.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to delete")

    try:
        project_translation_service.project_translation_repository.delete_project_translation(exist_project_translation)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    status_code = status.HTTP_200_OK
    data = {
        'project_id': project_id,
        'language_id': language_id,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response