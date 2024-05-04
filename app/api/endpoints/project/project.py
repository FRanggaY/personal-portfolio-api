from datetime import date
from fastapi import APIRouter, Depends, Form, Query, Request, UploadFile, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.response import GeneralDataPaginateResponse, GeneralDataResponse
from app.models.role_authority import RoleAuthorityFeature, RoleAuthorityName
from app.models.project.project import Project
from app.services.role_authority_service import RoleAuthorityService
from app.services.project.project_service import ProjectService
from app.services.company.company_service import CompanyService
from app.services.user_service import UserService
from app.utils.authentication import Authentication
from app.utils.handling_file import validation_file
from app.utils.manual import get_total_pages

router = APIRouter()

@router.post("", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    company_id: str = Form(..., min_length=1, max_length=36),
    title: str = Form(..., min_length=1, max_length=128),
    image: UploadFile = None,
    logo: UploadFile = None,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Create Project

        - should login
        - allow to create with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    company_service = CompanyService(db)
    project_service = ProjectService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.project.value, name=RoleAuthorityName.create.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to create")

    # validation
    exist_company = company_service.company_repository.read_company(company_id)
    if not exist_company:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company not exist")
    
    try:
        if (image):
            await validation_file(file=image)
        
        if (logo):
            await validation_file(file=logo)

        content_type_image = image.content_type if image else ""
        file_extension_image = content_type_image.split('/')[1] if image else ""
        
        content_type_logo = logo.content_type if logo else ""
        file_extension_logo = content_type_logo.split('/')[1] if logo else ""
        
        project_model = Project(
            company_id=company_id,
            user_id=user_id_active,
            title=title,
        )

        data = project_service.create_project(
            project_model,
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
def read_projects(
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
        Read All Project

        - need login

        - when has authority create other it show project information
        - when no has authority, it only show project it self
    """
    user_id_active = payload.get("uid", None)
    project_service = ProjectService(db)

    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)

    user_id_filter = user_id_active
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.project_other.value, name=RoleAuthorityName.create.value)
    if role_authority:
        user_id_filter = None

    base_url = str(request.base_url) if request else ""
    custom_filters = {filter_by_column: filter_value} if filter_by_column and filter_value else None

    projects = project_service.project_repository.read_projects(
        offset=offset, 
        size=size, 
        sort_by=sort_by, 
        sort_order=sort_order, 
        custom_filters=custom_filters,
        is_active=is_active,
        user_id=user_id_filter,
    )

    if not projects:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")
    
    count = project_service.project_repository.count_projects(
        custom_filters=custom_filters,
        is_active=is_active,
        user_id=user_id_filter,
    )
    total_pages = get_total_pages(size, count)
    

    datas = []
    for project in projects:
        company = {
            'id': project.company.id,
            'name': project.company.name,
        } if project.company else None
        datas.append({
            'id': project.id,
            'name': company,
            'title': project.title,
            'is_active': project.is_active,
            'created_at': str(project.created_at),
            'updated_at': str(project.updated_at),
            'image_url': f"{base_url}{project_service.static_folder_image}/{project.image_url}" if project.image_url else None,
            'logo_url': f"{base_url}{project_service.static_folder_logo}/{project.logo_url}" if project.logo_url else None,
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

@router.get("/{project_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
def read_project(
    project_id: str,
    request: Request,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read Project

        - should login

        - when has authority view other it show project information
        - when no has authority, it only show project it self
    """
    user_id_active = payload.get("uid", None)
    project_service = ProjectService(db)

    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)

    user_id_filter = user_id_active
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.project_other.value, name=RoleAuthorityName.view.value)
    if role_authority:
        user_id_filter = None

    base_url = str(request.base_url) if request else ""
    project = project_service.project_repository.read_project(project_id)

    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

    if not user_id_filter and project.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to read")
   
    company = {
        'id': project.company.id,
        'name': project.company.name,
    } if project.company else None

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data={
            'id': project.id,
            'name': company,
            'title': project.title,
            'is_active': project.is_active,
            'created_at': str(project.created_at),
            'updated_at': str(project.updated_at),
            'image_url': f"{base_url}{project_service.static_folder_image}/{project.image_url}" if project.image_url else None,
            'logo_url': f"{base_url}{project_service.static_folder_logo}/{project.logo_url}" if project.logo_url else None,
        },
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.patch("/{project_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def update_project(
    project_id: str,
    company_id: str = Form(..., min_length=1, max_length=36),
    title: str = Form(None, min_length=0, max_length=128),
    image: UploadFile = None,
    logo: UploadFile = None,
    is_active: bool = Form(default=True),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Update Project
        
        - should login
        - allow to update with role that has authority

        - when has authority edit other it allow edit project other
        - when no has authority, it only edit project it self
    """
    user_id_active = payload.get("uid", None)

    # service
    company_service = CompanyService(db)
    project_service = ProjectService(db)
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
    exist_project = project_service.project_repository.read_project(project_id)
    if not exist_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    exist_company = company_service.company_repository.read_company(company_id)
    if not exist_company:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company not exist")
    
    if not user_id_filter and exist_project.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update")

    try:
        if (image):
            await validation_file(file=image)
        
        if (logo):
            await validation_file(file=logo)

        content_type_image = image.content_type if image else ""
        file_extension_image = content_type_image.split('/')[1] if image else ""
        
        content_type_logo = logo.content_type if logo else ""
        file_extension_logo = content_type_logo.split('/')[1] if logo else ""

        project_model = Project(
            id=project_id,
            company_id=company_id,
            title=title,
            is_active=is_active,
        )

        data = project_service.update_project(
            exist_project,
            project_model,
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


@router.delete("/{project_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def delete_project(
    project_id: str,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Delete Project
        
        - should login
        - allow to delete with role that has authority

        - when has authority delete other it allow delete project other
        - when no has authority, it only delete project it self
    """
    user_id_active = payload.get("uid", None)

    # service
    project_service = ProjectService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.project.value, name=RoleAuthorityName.delete.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to delete")
    
    exist_project = project_service.project_repository.read_project(project_id)
    if not exist_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.project_other.value, name=RoleAuthorityName.delete.value)
    if role_authority:
        user_id_filter = None
    
    if not user_id_filter and exist_project.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to delete")

    try:
        project_service.delete_project(project_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    status_code = status.HTTP_200_OK
    data = {
        'id': project_id,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.get("-resource", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def read_project_resource(
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        List access control list for resource project based role id

        - should login
    """
    user_id_active = payload.get("uid", None)
    
    # get service
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)

    user_active = user_service.user_repository.read_user(user_id_active)

    # list
    role_authorities = role_authority_service.role_authority_repository.read_role_authorities(role_id=user_active.role_id, feature=[RoleAuthorityFeature.project.value, RoleAuthorityFeature.project_other.value])
    role_authority_list = [role_authority.name for role_authority in role_authorities] if role_authorities else []

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=role_authority_list,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response