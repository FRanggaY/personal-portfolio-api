from datetime import date
from fastapi import APIRouter, Depends, Form, Query, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.response import GeneralDataPaginateResponse, GeneralDataResponse
from app.models.role_authority import RoleAuthorityFeature, RoleAuthorityName
from app.models.skill.skill_mapping import SkillMapping
from app.services.role_authority_service import RoleAuthorityService
from app.services.skill.skill_mapping_service import SkillMappingService
from app.services.skill.skill_service import SkillService
from app.services.user_service import UserService
from app.utils.authentication import Authentication
from app.utils.manual import get_total_pages

router = APIRouter()

@router.post("", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
async def create_skill_mapping(
    skill_id: str = Form(..., min_length=1, max_length=36),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Create Skill Mapping

        - should login
        - allow to create with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    skill_service = SkillService(db)
    skill_mapping_service = SkillMappingService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.skill.value, name=RoleAuthorityName.create.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to create")

    # validation
    exist_skill = skill_service.skill_repository.read_skill(skill_id)
    if not exist_skill:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Skill not exist")
    
    exist_personal_skill = skill_mapping_service.skill_mapping_repository.get_skill_mapping_by_personal(skill_id, user_id_active)
    if exist_personal_skill:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Skill already assign")

    try:
        skill_mapping_model = SkillMapping(
            skill_id=skill_id,
            user_id=user_id_active,
        )

        data = skill_mapping_service.skill_mapping_repository.create_skill_mapping(
            skill_mapping_model,
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
def read_skill_mappings(
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
        Read All Skill Mapping

        - need login

        - when has authority create other it show skill information
        - when no has authority, it only show skill it self
    """
    user_id_active = payload.get("uid", None)
    skill_mapping_service = SkillMappingService(db)

    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)

    user_id_filter = user_id_active
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.skill_other.value, name=RoleAuthorityName.create.value)
    if role_authority:
        user_id_filter = None

    custom_filters = {filter_by_column: filter_value} if filter_by_column and filter_value else None

    skill_mappings = skill_mapping_service.skill_mapping_repository.read_skill_mappings(
        offset=offset, 
        size=size, 
        sort_by=sort_by, 
        sort_order=sort_order, 
        custom_filters=custom_filters,
        is_active=is_active,
        user_id=user_id_filter,
    )

    if not skill_mappings:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")
    
    count = skill_mapping_service.skill_mapping_repository.count_skill_mappings(
        custom_filters=custom_filters,
        is_active=is_active,
        user_id=user_id_filter,
    )
    total_pages = get_total_pages(size, count)
    

    datas = []
    for skill_mapping in skill_mappings:
        skill = {
            'id': skill_mapping.skill.id,
            'name': skill_mapping.skill.name,
        } if skill_mapping.skill else None
        datas.append({
            'id': skill_mapping.id,
            'name': skill,
            'is_active': skill_mapping.is_active,
            'created_at': str(skill_mapping.created_at),
            'updated_at': str(skill_mapping.updated_at),
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

@router.get("/{skill_mapping_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
def read_skill_mapping(
    skill_mapping_id: str,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read Skill Mapping

        - should login

        - when has authority view other it show skill information
        - when no has authority, it only show skill it self
    """
    user_id_active = payload.get("uid", None)
    skill_mapping_service = SkillMappingService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)

    user_id_filter = user_id_active
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.experience_other.value, name=RoleAuthorityName.view.value)
    if role_authority:
        user_id_filter = None

    skill_mapping = skill_mapping_service.skill_mapping_repository.read_skill_mapping(skill_mapping_id)

    if not skill_mapping:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

    if not user_id_filter and skill_mapping.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to read")
   
    skill = {
        'id': skill_mapping.skill.id,
        'name': skill_mapping.skill.name,
    } if skill_mapping.skill else None

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data={
            'id': skill_mapping.id,
            'name': skill,
            'is_active': skill_mapping.is_active,
            'created_at': str(skill_mapping.created_at),
            'updated_at': str(skill_mapping.updated_at),
        },
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.patch("/{skill_mapping_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def update_skill_mapping(
    skill_mapping_id: str,
    is_active: bool = Form(default=True),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Update Skill Mapping
        
        - should login
        - allow to update with role that has authority

        - when has authority edit other it allow edit skill other
        - when no has authority, it only edit skill it self
    """
    user_id_active = payload.get("uid", None)

    # service
    skill_mapping_service = SkillMappingService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.skill.value, name=RoleAuthorityName.edit.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to edit")
    
    # validation
    exist_skill_mapping = skill_mapping_service.skill_mapping_repository.read_skill_mapping(skill_mapping_id)
    if not exist_skill_mapping:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill Mapping not found")
    
    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.skill_other.value, name=RoleAuthorityName.edit.value)
    if role_authority:
        user_id_filter = None
    
    if not user_id_filter and exist_skill_mapping.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update")

    try:
        skill_mapping_model = SkillMapping(
            id=skill_mapping_id,
            is_active=is_active,
        )

        data = skill_mapping_service.update_skill_mapping(
            exist_skill_mapping,
            skill_mapping_model,
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


@router.delete("/{skill_mapping_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def delete_skill_mapping(
    skill_mapping_id: str,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Delete Skill Mapping
        
        - should login
        - allow to delete with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    skill_mapping_service = SkillMappingService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.skill.value, name=RoleAuthorityName.delete.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to delete")
    
    exist_skill_mapping = skill_mapping_service.skill_mapping_repository.read_skill_mapping(skill_mapping_id)
    if not exist_skill_mapping:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill Mapping not found")
    
    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.skill_other.value, name=RoleAuthorityName.delete.value)
    if role_authority:
        user_id_filter = None

    if not user_id_filter and exist_skill_mapping.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to delete")

    try:
        skill_mapping_service.skill_mapping_repository.delete_skill_mapping(exist_skill_mapping)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    status_code = status.HTTP_200_OK
    data = {
        'id': skill_mapping_id,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response