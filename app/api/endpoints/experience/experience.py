from datetime import date
from fastapi import APIRouter, Depends, Form, Query, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.response import GeneralDataPaginateResponse, GeneralDataResponse
from app.models.role_authority import RoleAuthorityFeature, RoleAuthorityName
from app.models.experience.experience import Experience
from app.services.role_authority_service import RoleAuthorityService
from app.services.experience.experience_service import ExperienceService
from app.services.company.company_service import CompanyService
from app.services.user_service import UserService
from app.utils.authentication import Authentication
from app.utils.manual import get_total_pages

router = APIRouter()

@router.post("", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
async def create_experience(
    company_id: str = Form(..., min_length=1, max_length=36),
    title: str = Form(..., min_length=1, max_length=128),
    started_at: date = Form(...),
    finished_at: date = Form(...),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Create Experience

        - should login
        - allow to create with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    company_service = CompanyService(db)
    experience_service = ExperienceService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.experience.value, name=RoleAuthorityName.create.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to create")

    # validation
    exist_company = company_service.company_repository.read_company(company_id)
    if not exist_company:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company not exist")
    
    try:
        experience_model = Experience(
            company_id=company_id,
            user_id=user_id_active,
            title=title,
            started_at=started_at,
            finished_at=finished_at,
        )

        data = experience_service.experience_repository.create_experience(
            experience_model,
        )
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

@router.get("", response_model=GeneralDataPaginateResponse, status_code=status.HTTP_200_OK)
def read_experiences(
    sort_by: str = Query(None),
    sort_order: str = Query(None),
    filter_by_column: str = Query(None),
    filter_value: str = Query(None),
    is_active: bool = Query(None),
    offset: int = Query(None, ge=1), 
    size: int = Query(None, ge=1),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read All Experience

        - need login

        - when has authority create other it show experience information
        - when no has authority, it only show experience it self
    """
    user_id_active = payload.get("uid", None)
    experience_service = ExperienceService(db)

    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)

    user_id_filter = user_id_active
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.experience_other.value, name=RoleAuthorityName.create.value)
    if role_authority:
        user_id_filter = None

    custom_filters = {filter_by_column: filter_value} if filter_by_column and filter_value else None

    experiences = experience_service.experience_repository.read_experiences(
        offset=offset, 
        size=size, 
        sort_by=sort_by, 
        sort_order=sort_order, 
        custom_filters=custom_filters,
        is_active=is_active,
        user_id=user_id_filter,
    )

    if not experiences:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")
    
    count = experience_service.experience_repository.count_experiences(
        custom_filters=custom_filters,
        is_active=is_active,
        user_id=user_id_filter,
    )
    total_pages = get_total_pages(size, count)
    

    datas = []
    for experience in experiences:
        company = {
            'id': experience.company.id,
            'name': experience.company.name,
        } if experience.company else None
        datas.append({
            'id': experience.id,
            'name': company,
            'title': experience.title,
            'is_active': experience.is_active,
            'started_at': str(experience.started_at),
            'finished_at': str(experience.finished_at),
            'created_at': str(experience.created_at),
            'updated_at': str(experience.updated_at),
        })

    status_code = status.HTTP_200_OK
    data_response = GeneralDataPaginateResponse(
        code=status_code,
        status="OK",
        data=datas,
        meta={
            "size": size,
            "total": count,
            "total_pages": total_pages,
            "offset": offset
        },
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.get("/{experience_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
def read_experience(
    experience_id: str,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read Experience

        - should login

        - when has authority view other it show experience information
        - when no has authority, it only show experience it self
    """
    user_id_active = payload.get("uid", None)
    experience_service = ExperienceService(db)

    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)

    user_id_filter = user_id_active
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.experience_other.value, name=RoleAuthorityName.view.value)
    if role_authority:
        user_id_filter = None

    experience = experience_service.experience_repository.read_experience(experience_id)

    if not experience:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

    if not user_id_filter and experience.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to read")
   
    company = {
        'id': experience.company.id,
        'name': experience.company.name,
    } if experience.company else None

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data={
            'id': experience.id,
            'name': company,
            'title': experience.title,
            'is_active': experience.is_active,
            'started_at': str(experience.started_at),
            'finished_at': str(experience.finished_at),
            'created_at': str(experience.created_at),
            'updated_at': str(experience.updated_at),
        },
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.patch("/{experience_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def update_experience(
    experience_id: str,
    company_id: str = Form(..., min_length=1, max_length=36),
    title: str = Form(None, min_length=0, max_length=128),
    started_at: date = Form(None),
    finished_at: date = Form(None),
    is_active: bool = Form(default=True),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Update Experience
        
        - should login
        - allow to update with role that has authority

        - when has authority edit other it allow edit experience other
        - when no has authority, it only edit experience it self
    """
    user_id_active = payload.get("uid", None)

    # service
    company_service = CompanyService(db)
    experience_service = ExperienceService(db)
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
    exist_experience = experience_service.experience_repository.read_experience(experience_id)
    if not exist_experience:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")
    
    exist_company = company_service.company_repository.read_company(company_id)
    if not exist_company:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company not exist")
    
    if not user_id_filter and exist_experience.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update")

    try:
        experience_model = Experience(
            id=experience_id,
            company_id=company_id,
            title=title,
            started_at=started_at,
            finished_at=finished_at,
            is_active=is_active,
        )

        data = experience_service.update_experience(
            exist_experience,
            experience_model,
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


@router.delete("/{experience_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def delete_experience(
    experience_id: str,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Delete Experience
        
        - should login
        - allow to delete with role that has authority

        - when has authority delete other it allow delete experience other
        - when no has authority, it only delete experience it self
    """
    user_id_active = payload.get("uid", None)

    # service
    experience_service = ExperienceService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.experience.value, name=RoleAuthorityName.delete.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to delete")
    
    exist_experience = experience_service.experience_repository.read_experience(experience_id)
    if not exist_experience:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Experience not found")

    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.experience_other.value, name=RoleAuthorityName.delete.value)
    if role_authority:
        user_id_filter = None
    
    if not user_id_filter and exist_experience.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to delete")

    try:
        experience_service.experience_repository.delete_experience(experience_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    status_code = status.HTTP_200_OK
    data = {
        'id': experience_id,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.get("-resource", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def read_experience_resource(
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        List access control list for resource experience based role id

        - should login
    """
    user_id_active = payload.get("uid", None)
    
    # get service
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)

    user_active = user_service.user_repository.read_user(user_id_active)

    # list
    role_authorities = role_authority_service.role_authority_repository.read_role_authorities(role_id=user_active.role_id, feature=[RoleAuthorityFeature.experience.value, RoleAuthorityFeature.experience_other.value])
    role_authority_list = [role_authority.name for role_authority in role_authorities] if role_authorities else []

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=role_authority_list,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response