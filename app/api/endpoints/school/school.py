from fastapi import APIRouter, Depends, Form, Query, Request, UploadFile, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.response import GeneralDataPaginateResponse, GeneralDataResponse
from app.models.role.role_authority import RoleAuthorityFeature, RoleAuthorityName
from app.models.school.school import School
from app.services.role.role_authority_service import RoleAuthorityService
from app.services.role.role_service import RoleService
from app.services.school.school_service import SchoolService
from app.services.user_service import UserService
from app.utils.authentication import Authentication
from app.utils.handling_file import validation_file
from app.utils.manual import get_total_pages

router = APIRouter()

@router.post("", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
async def create_school(
    code: str = Form(..., min_length=1, max_length=36),
    name: str = Form(..., min_length=1, max_length=36),
    website_url: str = Form(None, min_length=0, max_length=512),
    image: UploadFile = None,
    logo: UploadFile = None,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Create School

        - should login
        - allow to create with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    school_service = SchoolService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.school.value, name=RoleAuthorityName.create.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to create")

    # validation
    exist_code = school_service.school_repository.get_school_by_code(code)
    if exist_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code already exist")
    
    exist_name = school_service.school_repository.get_school_by_name(name)
    if exist_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Name already exist")
    
    try:
        if (image):
            await validation_file(file=image)
        
        if (logo):
            await validation_file(file=logo)

        content_type_image = image.content_type if image else ""
        file_extension_image = content_type_image.split('/')[1] if image else ""
        
        content_type_logo = logo.content_type if logo else ""
        file_extension_logo = content_type_logo.split('/')[1] if logo else ""

        school_model = School(
            code=code,
            name=name,
            website_url=website_url,
        )

        data = school_service.create_school(
            school_model,
            image,
            logo,
            file_extension_image,
            file_extension_logo
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
def read_schools(
    request: Request,
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
        Read All School

        - need login
    """
    school_service = SchoolService(db)

    base_url = str(request.base_url) if request else ""
    custom_filters = {filter_by_column: filter_value} if filter_by_column and filter_value else None

    schools = school_service.school_repository.read_schools(
        offset=offset, 
        size=size, 
        sort_by=sort_by, 
        sort_order=sort_order, 
        custom_filters=custom_filters,
        is_active=is_active
    )

    if not schools:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")
    
    count = school_service.school_repository.count_schools(
        custom_filters=custom_filters,
        is_active=is_active
    )
    total_pages = get_total_pages(size, count)
    

    datas = []
    for school in schools:
        datas.append({
            'id': school.id,
            'name': school.name,
            'code': school.code,
            'is_active': school.is_active,
            'created_at': str(school.created_at),
            'updated_at': str(school.updated_at),
            'image_url': f"{base_url}{school_service.static_folder_image}/{school.image_url}" if school.image_url else None,
            'logo_url': f"{base_url}{school_service.static_folder_logo}/{school.logo_url}" if school.logo_url else None,
            'website_url': str(school.website_url) if school.website_url else None,
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

@router.get("/{school_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
def read_school(
    school_id: str,
    request: Request,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read School

        - should login
    """
    school_service = SchoolService(db)
    base_url = str(request.base_url) if request else ""
    school = school_service.school_repository.read_school(school_id)

    if not school:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data={
            'id': school.id,
            'name': school.name,
            'code': school.code,
            'is_active': school.is_active,
            'created_at': str(school.created_at),
            'updated_at': str(school.updated_at),
            'image_url': f"{base_url}{school_service.static_folder_image}/{school.image_url}" if school.image_url else None,
            'logo_url': f"{base_url}{school_service.static_folder_logo}/{school.logo_url}" if school.logo_url else None,
            'website_url': str(school.website_url) if school.website_url else None,
        },
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.patch("/{school_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def update_school(
    school_id: str,
    code: str = Form(None, min_length=0, max_length=36),
    name: str = Form(None, min_length=0, max_length=36),
    website_url: str = Form(None, min_length=0, max_length=256),
    is_active: bool = Form(default=True),
    image: UploadFile = None,
    logo: UploadFile = None,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Update School
        
        - should login
        - allow to update with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    school_service = SchoolService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.school.value, name=RoleAuthorityName.edit.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to edit")
    
    # validation
    exist_school = school_service.school_repository.read_school(school_id)
    if not exist_school:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="School not found")
    
    try:
        if (image):
            await validation_file(file=image)
        
        if (logo):
            await validation_file(file=logo)

        content_type_image = image.content_type if image else ""
        file_extension_image = content_type_image.split('/')[1] if image else ""
        
        content_type_logo = logo.content_type if logo else ""
        file_extension_logo = content_type_logo.split('/')[1] if logo else ""

        school_model = School(
            id=school_id,
            code=code,
            name=name,
            website_url=website_url,
            is_active=is_active,
        )

        data = school_service.update_school(
            exist_school,
            school_model,
            image,
            logo,
            file_extension_image,
            file_extension_logo
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


@router.delete("/{school_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def delete_school(
    school_id: str,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Delete School
        
        - should login
        - allow to delete with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    school_service = SchoolService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.school.value, name=RoleAuthorityName.delete.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to delete")

    try:
        school_service.delete_school(school_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    status_code = status.HTTP_200_OK
    data = {
        'id': school_id,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.get("-resource", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def read_school_resource(
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        List access control list for resource school based role id

        - should login
    """
    user_id_active = payload.get("uid", None)
    
    # get service
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)

    user_active = user_service.user_repository.read_user(user_id_active)

    # list
    role_authorities = role_authority_service.role_authority_repository.read_role_authorities(role_id=user_active.role_id, feature=RoleAuthorityFeature.school.value)
    role_authority_list = [role_authority.name for role_authority in role_authorities] if role_authorities else []

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=role_authority_list,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response