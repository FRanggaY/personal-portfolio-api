from fastapi import APIRouter, Depends, Form, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import LanguageOption
from app.models.response import GeneralDataResponse
from app.models.role.role_authority import RoleAuthorityFeature, RoleAuthorityName
from app.models.solution.solution_translation import SolutionTranslation
from app.services.solution.solution_service import SolutionService
from app.services.role.role_authority_service import RoleAuthorityService
from app.services.solution.solution_translation_service import SolutionTranslationService
from app.services.user_service import UserService
from app.utils.authentication import Authentication

router = APIRouter()

@router.post("", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
async def create_solution_translation(
    solution_id: str = Form(..., min_length=1, max_length=36),
    language_id: LanguageOption = Form(...),
    title: str = Form(..., min_length=1, max_length=128),
    description: str = Form(None, min_length=0, max_length=512),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Create Solution Translation

        - should login
        - allow to create with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    solution_translation_service = SolutionTranslationService(db)
    solution_service = SolutionService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.solution.value, name=RoleAuthorityName.create.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to create")

    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.solution_other.value, name=RoleAuthorityName.create.value)
    if role_authority:
        user_id_filter = None

    language_id = language_id.value

    # validation
    exist_solution = solution_service.solution_repository.read_solution(solution_id)
    if not exist_solution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solution not found")
    
    if user_id_filter is not None and exist_solution.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to create")

    exist_data = solution_translation_service.solution_translation_repository.get_solution_translation_by_solution_id_and_language_id(solution_id=solution_id, language_id=language_id)
    if exist_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Solution Translation already exist")
    
    try:
        solution_translation_model = SolutionTranslation(
            language_id=language_id,
            solution_id=solution_id,
            description=description,
            title=title,
        )

        data = solution_translation_service.solution_translation_repository.create_solution_translation(solution_translation_model)
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

@router.get("/{solution_id}/{language_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
def read_solution_translation(
    solution_id: str,
    language_id: LanguageOption,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read Solution Translation

        - should login
    """
    user_id_active = payload.get("uid", None)
    solution_translation_service = SolutionTranslationService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)

    user_id_filter = user_id_active

    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.solution_other.value, name=RoleAuthorityName.view.value)
    if role_authority:
        user_id_filter = None

    solution_translation = solution_translation_service.solution_translation_repository.get_solution_translation_by_solution_id_and_language_id(solution_id=solution_id, language_id=language_id.value)
    
    if not solution_translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

    if user_id_filter is not None and solution_translation.solution.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to read")

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data={
            'id': solution_translation.id,
            'title': solution_translation.title,
            'description': solution_translation.description,
            'language_id': solution_translation.language_id,
            'created_at': str(solution_translation.created_at),
            'updated_at': str(solution_translation.updated_at),
        },
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.patch("/{solution_id}/{language_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def update_solution_translation(
    solution_id: str,
    language_id: LanguageOption,
    title: str = Form(None, min_length=1, max_length=128),
    description: str = Form(None, min_length=0, max_length=512),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Update Solution Translation
        
        - should login
        - allow to update with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    solution_translation_service = SolutionTranslationService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.solution.value, name=RoleAuthorityName.edit.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to edit")
    
    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.solution_other.value, name=RoleAuthorityName.edit.value)
    if role_authority:
        user_id_filter = None

    # validation
    exist_solution_translation = solution_translation_service.solution_translation_repository.get_solution_translation_by_solution_id_and_language_id(solution_id=solution_id, language_id=language_id.value)
    if not exist_solution_translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solution Translation not found")
    
    if user_id_filter is not None and exist_solution_translation.solution.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update")

    try:
        solution_translation_model = SolutionTranslation(
            id=exist_solution_translation.id,
            language_id=language_id.value,
            solution_id=solution_id,
            description=description,
            title=title,
        )

        data = solution_translation_service.update_solution_translation(
            exist_solution_translation,
            solution_translation_model,
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


@router.delete("/{solution_id}/{language_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def delete_solution_translation(
    solution_id: str,
    language_id: LanguageOption,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Delete SolutionTranslation
        
        - should login
        - allow to delete with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    solution_translation_service = SolutionTranslationService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.solution.value, name=RoleAuthorityName.delete.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to delete")

    exist_solution_translation = solution_translation_service.solution_translation_repository.get_solution_translation_by_solution_id_and_language_id(solution_id, language_id)
    if not exist_solution_translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solution not found")

    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.solution_other.value, name=RoleAuthorityName.delete.value)
    if role_authority:
        user_id_filter = None

    if user_id_filter is not None and exist_solution_translation.solution.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to delete")

    try:
        solution_translation_service.solution_translation_repository.delete_solution_translation(exist_solution_translation)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    status_code = status.HTTP_200_OK
    data = {
        'solution_id': solution_id,
        'language_id': language_id,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response