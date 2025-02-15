from fastapi import APIRouter, Depends, Form, Query,status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.dtos.role import CreateRole, EditRole
from app.models.response import GeneralDataPaginateResponse, GeneralDataResponse
from app.models.role.role import Role
from app.models.role.role_authority import RoleAuthorityFeature, RoleAuthorityName
from app.services.role.role_authority_service import RoleAuthorityService
from app.services.role.role_service import RoleService
from app.services.user_service import UserService
from app.utils.authentication import Authentication
from app.utils.manual import get_total_pages

router = APIRouter()

@router.post("", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: CreateRole,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Create Role

        - should login
        - allow to create with role that has authority
    """
    user_id = payload.get("uid", None)

    # service
    user_service = UserService(db)
    role_authority_service = RoleAuthorityService(db)
    role_service = RoleService(db)
    
    user_active = user_service.user_repository.read_user(user_id)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.role.value, name=RoleAuthorityName.create.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to create")

    # validation
    exist_code = role_service.role_repository.get_role_by_code(data.code)
    if exist_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code already exist")
    
    exist_name = role_service.role_repository.get_role_by_name(data.name)
    if exist_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name already exist")
    
    try:
        role_model = Role(
            code=data.code,
            level=data.level,
            name=data.name,
            description=data.description,
        )

        data = role_service.role_repository.create_role(role_model)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    
    status_code = status.HTTP_201_CREATED
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

@router.get("", response_model=GeneralDataPaginateResponse, status_code=status.HTTP_200_OK)
def read_roles(
    offset: int = Query(None, ge=1), 
    size: int = Query(None, ge=1),
    is_active: bool = Query(None),
    sort_by: str = Query(None),
    sort_order: str = Query(None),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read All Role

        - should login
        - filter role by level that user login
    """
    user_id = payload.get('uid', None)
    user_service = UserService(db)
    role_service = RoleService(db)

    user = user_service.user_repository.read_user(user_id)
    level = user.role.level if user.role else None
    
    roles = role_service.role_repository.read_roles(
        offset=offset, 
        size=size,
        is_active=is_active,
        level=level,
        sort_by=sort_by,
        sort_order=sort_order,
    )

    if not roles:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")
    
    count = role_service.role_repository.count_roles(
        is_active=is_active, 
        level=level,
    )
    total_pages = get_total_pages(size, count)
    

    datas = []
    for role in roles:
        datas.append({
            'id': role.id,
            'code': role.code,
            'level': role.level,
            'name': role.name,
            'description': role.description,
            'is_active': role.is_active,
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

@router.get("/{role_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
def read_role(
    role_id: str,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read Role

        - should login
    """
    role_service = RoleService(db)
    role = role_service.role_repository.read_role(role_id)

    if not role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data={
            'id': role.id,
            'code': role.code,
            'level': role.level,
            'name': role.name,
            'description': role.description,
            'is_active': role.is_active,
        },
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.patch("/{role_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def update_role(
    role_id: str,
    data: EditRole,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Update Role

        - should login
        - allow to update with role that has authority
    """
    user_id = payload.get("uid", None)

    # service
    user_service = UserService(db)
    role_authority_service = RoleAuthorityService(db)
    role_service = RoleService(db)
    
    user_active = user_service.user_repository.read_user(user_id)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.role.value, name=RoleAuthorityName.edit.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to edit")
    
    # validation
    exist_role = role_service.role_repository.read_role(role_id)
    if not exist_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    try:
        role_model = Role(
            id=role_id,
            code=data.code,
            name=data.name,
            level=data.level,
            description=data.description,
            is_active=data.is_active,
        )

        data = role_service.update_role(
            exist_role,
            role_model
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

@router.delete("/{role_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def delete_role(
    role_id: str,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Delete Role
        
        If user still have using this role, throw bad request that should clear user with the selected role
        - should login
        - allow to delete with role that has authority
    """
    user_id = payload.get("uid", None)

    # service
    user_service = UserService(db)
    role_authority_service = RoleAuthorityService(db)
    role_service = RoleService(db)
    
    user_active = user_service.user_repository.read_user(user_id)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.role.value, name=RoleAuthorityName.delete.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to delete")

    try:
        count_user = user_service.user_repository.count_users(role_id=role_id)
        if count_user > 0:
            raise ValueError("Clear user with this role before deleting this role")
        role_service.delete_role(role_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    status_code = status.HTTP_200_OK
    data = {
        'id': role_id,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.get("-resource", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def read_role_resource(
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        List access control list for resource role based role id

        - should login
    """
    user_id = payload.get("uid", None)
    
    # get service
    user_service = UserService(db)
    role_authority_service = RoleAuthorityService(db)

    user_active = user_service.user_repository.read_user(user_id)

    # list
    role_authorities = role_authority_service.role_authority_repository.read_role_authorities(role_id=user_active.role_id, feature=RoleAuthorityFeature.role.value)
    role_authority_list = [role_authority.name for role_authority in role_authorities] if role_authorities else []

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=role_authority_list,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response