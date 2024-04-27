from fastapi import APIRouter, Depends, Form, Query, Request, UploadFile, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.response import GeneralDataPaginateResponse, GeneralDataResponse
from app.models.role_authority import RoleAuthorityFeature, RoleAuthorityName
from app.models.user import User, UserGender
from app.services.role_authority_service import RoleAuthorityService
from app.services.role_service import RoleService
from app.services.user_service import UserService
from app.utils.authentication import Authentication
from app.utils.handling_file import validation_file
from app.utils.manual import get_total_pages

router = APIRouter()

@router.post("", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    role_id: int = Form(...),
    username: str = Form(..., min_length=1, max_length=36),
    email: str = Form(..., min_length=1, max_length=36),
    password: str = Form(..., min_length=1, max_length=512),
    name: str = Form(..., min_length=1, max_length=36),
    no_handphone: str = Form(None, min_length=0, max_length=256),
    gender: UserGender = Form(...),
    image: UploadFile = None,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Create User

        - should login
        - allow to create with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    user_service = UserService(db)
    role_authority_service = RoleAuthorityService(db)
    role_service = RoleService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.user.value, name=RoleAuthorityName.create.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to create")

    # validation
    exist_role_id = role_service.role_repository.read_role(role_id)
    if not exist_role_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    exist_username = user_service.user_repository.get_user_by_username(username)
    if exist_username:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exist")
    
    exist_email = user_service.user_repository.get_user_by_email(email)
    if exist_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exist")
    
    try:
        if (image):
            await validation_file(file=image)

        content_type = image.content_type if image else ""
        file_extension = content_type.split('/')[1] if image else ""

        user_model = User(
            role_id=role_id,
            username=username,
            email=email,
            name=name,
            password=user_service.get_password_hash(password),
            no_handphone=no_handphone,
            gender=gender.value,
        )

        data = user_service.create_user(
            user_model,
            image,
            file_extension,
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
def read_users(
    request: Request,
    role_id: int = Query(None),
    sort_by: str = Query(None),
    sort_order: str = Query(None),
    filter_by_column: str = Query(None),
    filter_value: str = Query(None),
    is_role_level: bool = Query(None),
    is_active: bool = Query(None),
    offset: int = Query(None, ge=1), 
    size: int = Query(None, ge=1),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read All User

        - need login
        - has leveling that show only user with range level

        - if has access to view it show all user
        - if no has access to view it only show his user itself
    """
    user_id_active = payload.get('uid', None)
    user_service = UserService(db)
    role_authority_service = RoleAuthorityService(db)

    base_url = str(request.base_url) if request else ""
    custom_filters = {filter_by_column: filter_value} if filter_by_column and filter_value else None
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_level = user_active.role.level if user_active.role else None

    user_id = None
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.user.value, name=RoleAuthorityName.view.value)
    if not role_authority:
        user_id =  user_active.id

    users = user_service.user_repository.read_users(
        role_id=role_id, 
        offset=offset, 
        size=size, 
        sort_by=sort_by, 
        sort_order=sort_order, 
        custom_filters=custom_filters,
        role_level=role_level,
        is_role_level=is_role_level,
        user_id=user_id,
        is_active=is_active
    )

    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")
    
    count = user_service.user_repository.count_users(
        role_id=role_id, 
        custom_filters=custom_filters,
        role_level=role_level,
        is_role_level=is_role_level,
        user_id=user_id,
        is_active=is_active
    )
    total_pages = get_total_pages(size, count)
    

    datas = []
    for user in users:
        role = {
            'id': user.role.id,
            'name': user.role.name,
            'is_active': user.role.is_active,
        } if user.role else {}
        datas.append({
            'id': user.id,
            'name': user.name,
            'gender': user.gender,
            'role': role,
            'is_active': user.is_active,
            'last_login_at': str(user.last_login_at),
            'created_at': str(user.created_at),
            'updated_at': str(user.updated_at),
            'image_url': f"{base_url}{user_service.static_folder_image}/{user.image_url}" if user.image_url else None,
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

@router.get("/{user_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
def read_user(
    user_id: str,
    request: Request,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read User

        - should login
    """
    user_service = UserService(db)
    base_url = str(request.base_url) if request else ""
    user = user_service.user_repository.read_user(user_id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

    role = {
        'id': user.role.id,
        'name': user.role.name,
        'is_active': user.role.is_active,
    } if user.role else {}

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data={
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'name': user.name,
            'gender': user.gender,
            'role': role,
            'no_handphone': user.no_handphone,
            'is_active': user.is_active,
            'last_login_at': str(user.last_login_at),
            'created_at': str(user.created_at),
            'updated_at': str(user.updated_at),
            'image_url': f"{base_url}{user_service.static_folder_image}/{user.image_url}" if user.image_url else None,
        },
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.patch("/{user_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def update_user(
    user_id: str,
    role_id: int = Form(...),
    username: str = Form(None, min_length=0, max_length=36),
    email: str = Form(None, min_length=0, max_length=36),
    name: str = Form(None, min_length=0, max_length=36),
    no_handphone: str = Form(None, min_length=0, max_length=256),
    is_active: bool = Form(default=True),
    gender: UserGender = Form(...),
    image: UploadFile = None,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Update User
        
        - should login
        - allow to update with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    user_service = UserService(db)
    role_authority_service = RoleAuthorityService(db)
    role_service = RoleService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.user.value, name=RoleAuthorityName.edit.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to edit")
    
    # validation
    exist_role_id = role_service.role_repository.read_role(role_id)
    if not exist_role_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    
    exist_user = user_service.user_repository.read_user(user_id)
    if not exist_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    try:
        if (image):
            await validation_file(file=image)

        content_type = image.content_type if image else ""
        file_extension = content_type.split('/')[1] if image else ""

        user_model = User(
            id=user_id,
            role_id=role_id,
            username=username,
            email=email,
            name=name,
            no_handphone=no_handphone,
            gender=gender.value,
            is_active=is_active,
        )

        data = user_service.update_user(
            exist_user,
            user_model,
            image,
            file_extension,
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


@router.delete("/{user_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Delete User
        
        - should login
        - allow to delete with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    user_service = UserService(db)
    role_authority_service = RoleAuthorityService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.user.value, name=RoleAuthorityName.delete.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to delete")

    try:
        user_service.delete_user(user_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    status_code = status.HTTP_200_OK
    data = {
        'id': user_id,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.get("-resource", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def read_user_resource(
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        List access control list for resource user based role id

        - should login
    """
    user_id_active = payload.get("uid", None)
    
    # get service
    user_service = UserService(db)
    role_authority_service = RoleAuthorityService(db)

    user_active = user_service.user_repository.read_user(user_id_active)

    # list
    role_authorities = role_authority_service.role_authority_repository.read_role_authorities(role_id=user_active.role_id, feature=RoleAuthorityFeature.user.value)
    role_authority_list = [role_authority.name for role_authority in role_authorities] if role_authorities else []

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=role_authority_list,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response