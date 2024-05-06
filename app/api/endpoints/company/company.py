from fastapi import APIRouter, Depends, Form, Query, Request, UploadFile, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.response import GeneralDataPaginateResponse, GeneralDataResponse
from app.models.role_authority import RoleAuthorityFeature, RoleAuthorityName
from app.models.company.company import Company
from app.services.role_authority_service import RoleAuthorityService
from app.services.role_service import RoleService
from app.services.company.company_service import CompanyService
from app.services.user_service import UserService
from app.utils.authentication import Authentication
from app.utils.handling_file import validation_file
from app.utils.manual import get_total_pages

router = APIRouter()

@router.post("", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    code: str = Form(..., min_length=1, max_length=36),
    name: str = Form(..., min_length=1, max_length=36),
    website_url: str = Form(None, min_length=0, max_length=512),
    image: UploadFile = None,
    logo: UploadFile = None,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Create Company

        - should login
        - allow to create with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    company_service = CompanyService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.company.value, name=RoleAuthorityName.create.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to create")

    # validation
    exist_code = company_service.company_repository.get_company_by_code(code)
    if exist_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code already exist")
    
    exist_name = company_service.company_repository.get_company_by_name(name)
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

        company_model = Company(
            code=code,
            name=name,
            website_url=website_url,
        )

        data = company_service.create_company(
            company_model,
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
def read_companies(
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
        Read All Company

        - need login
    """
    company_service = CompanyService(db)

    base_url = str(request.base_url) if request else ""
    custom_filters = {filter_by_column: filter_value} if filter_by_column and filter_value else None

    companies = company_service.company_repository.read_companies(
        offset=offset, 
        size=size, 
        sort_by=sort_by, 
        sort_order=sort_order, 
        custom_filters=custom_filters,
        is_active=is_active
    )

    if not companies:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")
    
    count = company_service.company_repository.count_companies(
        custom_filters=custom_filters,
        is_active=is_active
    )
    total_pages = get_total_pages(size, count)
    

    datas = []
    for company in companies:
        datas.append({
            'id': company.id,
            'name': company.name,
            'code': company.code,
            'is_active': company.is_active,
            'created_at': str(company.created_at),
            'updated_at': str(company.updated_at),
            'image_url': f"{base_url}{company_service.static_folder_image}/{company.image_url}" if company.image_url else None,
            'logo_url': f"{base_url}{company_service.static_folder_logo}/{company.logo_url}" if company.logo_url else None,
            'website_url': str(company.website_url) if company.website_url else None,
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

@router.get("/{company_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
def read_company(
    company_id: str,
    request: Request,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read Company

        - should login
    """
    company_service = CompanyService(db)
    base_url = str(request.base_url) if request else ""
    company = company_service.company_repository.read_company(company_id)

    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data={
            'id': company.id,
            'name': company.name,
            'code': company.code,
            'is_active': company.is_active,
            'created_at': str(company.created_at),
            'updated_at': str(company.updated_at),
            'image_url': f"{base_url}{company_service.static_folder_image}/{company.image_url}" if company.image_url else None,
            'logo_url': f"{base_url}{company_service.static_folder_logo}/{company.logo_url}" if company.logo_url else None,
            'website_url': str(company.website_url) if company.website_url else None,
        },
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.patch("/{company_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def update_company(
    company_id: str,
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
        Update Company
        
        - should login
        - allow to update with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    company_service = CompanyService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.company.value, name=RoleAuthorityName.edit.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to edit")
    
    # validation
    exist_company = company_service.company_repository.read_company(company_id)
    if not exist_company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")
    
    try:
        if (image):
            await validation_file(file=image)
        
        if (logo):
            await validation_file(file=logo)

        content_type_image = image.content_type if image else ""
        file_extension_image = content_type_image.split('/')[1] if image else ""
        
        content_type_logo = logo.content_type if logo else ""
        file_extension_logo = content_type_logo.split('/')[1] if logo else ""

        company_model = Company(
            id=company_id,
            code=code,
            name=name,
            website_url=website_url,
            is_active=is_active,
        )

        data = company_service.update_company(
            exist_company,
            company_model,
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


@router.delete("/{company_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def delete_company(
    company_id: str,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Delete Company
        
        - should login
        - allow to delete with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    company_service = CompanyService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.company.value, name=RoleAuthorityName.delete.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to delete")

    try:
        company_service.delete_company(company_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    status_code = status.HTTP_200_OK
    data = {
        'id': company_id,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.get("-resource", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def read_company_resource(
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        List access control list for resource company based role id

        - should login
    """
    user_id_active = payload.get("uid", None)
    
    # get service
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)

    user_active = user_service.user_repository.read_user(user_id_active)

    # list
    role_authorities = role_authority_service.role_authority_repository.read_role_authorities(role_id=user_active.role_id, feature=RoleAuthorityFeature.company.value)
    role_authority_list = [role_authority.name for role_authority in role_authorities] if role_authorities else []

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=role_authority_list,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response