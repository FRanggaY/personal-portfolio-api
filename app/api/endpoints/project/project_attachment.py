from datetime import date
from fastapi import APIRouter, Depends, Form, Query, UploadFile, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.response import GeneralDataPaginateResponse, GeneralDataResponse
from app.models.role.role_authority import RoleAuthorityFeature, RoleAuthorityName
from app.models.project.project_attachment import ProjectAttachment
from app.services.role.role_authority_service import RoleAuthorityService
from app.services.project.project_attachment_service import ProjectAttachmentService
from app.services.project.project_service import ProjectService
from app.services.user_service import UserService
from app.utils.authentication import Authentication
from app.utils.handling_file import validation_file
from app.utils.manual import get_total_pages

router = APIRouter()

@router.post("", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
async def create_project_attachment(
    project_id: str = Form(..., min_length=1, max_length=36),
    title: str = Form(..., min_length=1, max_length=128),
    description: str = Form(None, min_length=0, max_length=512),
    website_url: str = Form(None, min_length=0, max_length=512),
    category: str = Form(..., min_length=1, max_length=512),
    image: UploadFile = None,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Create ProjectAttachment

        - should login
        - allow to create with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    project_service = ProjectService(db)
    project_attachment_service = ProjectAttachmentService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.project.value, name=RoleAuthorityName.create.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to create")

    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.project_other.value, name=RoleAuthorityName.create.value)
    if role_authority:
        user_id_filter = None

    # validation
    exist_project = project_service.project_repository.read_project(project_id)
    if not exist_project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    
    if user_id_filter is not None and exist_project.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to create")

    try:
        if (image):
            await validation_file(file=image)

        content_type_image = image.content_type if image else ""
        file_extension_image = content_type_image.split('/')[1] if image else ""
        
        project_attachment_model = ProjectAttachment(
            project_id=project_id,
            title=title,
            description=description,
            website_url=website_url,
            category=category,
        )

        data = project_attachment_service.create_project_attachment(
            project_attachment_model,
            exist_project,
            image,
            file_extension_image,
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
def read_project_attachments(
    project_id: str = Query(None),
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
        Read All ProjectAttachment

        - need login
    """
    project_attachment_service = ProjectAttachmentService(db)

    
    custom_filters = {filter_by_column: filter_value} if filter_by_column and filter_value else None

    project_attachments = project_attachment_service.project_attachment_repository.read_project_attachments(
        offset=offset, 
        size=size, 
        sort_by=sort_by, 
        sort_order=sort_order, 
        custom_filters=custom_filters,
        is_active=is_active,
        project_id=project_id
    )

    if not project_attachments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")
    
    count = project_attachment_service.project_attachment_repository.count_project_attachments(
        custom_filters=custom_filters,
        is_active=is_active,
        project_id=project_id
    )
    total_pages = get_total_pages(size, count)
    

    datas = []
    for project_attachment in project_attachments:
        datas.append({
            'id': project_attachment.id,
            'title': project_attachment.title,
            'is_active': project_attachment.is_active,
            'description': project_attachment.description if project_attachment.description else None,
            'website_url': project_attachment.website_url if project_attachment.website_url else None,
            'category': project_attachment.category,
            'created_at': str(project_attachment.created_at),
            'updated_at': str(project_attachment.updated_at),
            'image_url': f"{project_attachment_service.static_folder_image}/{project_attachment.image_url}" if project_attachment.image_url else None,
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

@router.get("/{project_attachment_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
def read_project_attachment(
    project_attachment_id: str,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read ProjectAttachment

        - should login

        - when has authority view other it show project_attachment information
        - when no has authority, it only show project_attachment it self
    """
    user_id_active = payload.get("uid", None)
    project_attachment_service = ProjectAttachmentService(db)

    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)

    user_id_filter = user_id_active
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.project.value, name=RoleAuthorityName.view.value)
    if role_authority:
        user_id_filter = None

    
    project_attachment = project_attachment_service.project_attachment_repository.read_project_attachment(project_attachment_id)

    if not project_attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

    if user_id_filter is not None and project_attachment.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to read")

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data={
            'id': project_attachment.id,
            'title': project_attachment.title,
            'is_active': project_attachment.is_active,
            'description': project_attachment.description if project_attachment.description else None,
            'website_url': project_attachment.website_url if project_attachment.website_url else None,
            'category': project_attachment.category,
            'created_at': str(project_attachment.created_at),
            'updated_at': str(project_attachment.updated_at),
            'image_url': f"{project_attachment_service.static_folder_image}/{project_attachment.image_url}" if project_attachment.image_url else None,
        },
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.patch("/{project_attachment_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def update_project_attachment(
    project_attachment_id: str,
    project_id: str = Form(..., min_length=1, max_length=36),
    title: str = Form(None, min_length=0, max_length=128),
    description: str = Form(None, min_length=0, max_length=512),
    website_url: str = Form(None, min_length=0, max_length=512),
    category: str = Form(None, min_length=0, max_length=512),
    image: UploadFile = None,
    is_active: bool = Form(default=True),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Update ProjectAttachment
        
        - should login
        - allow to update with role that has authority

        - when has authority edit other it allow edit project_attachment other
        - when no has authority, it only edit project_attachment it self
    """
    user_id_active = payload.get("uid", None)

    # service
    project_service = ProjectService(db)
    project_attachment_service = ProjectAttachmentService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.project.value, name=RoleAuthorityName.edit.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to edit")
    
    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.project.value, name=RoleAuthorityName.edit.value)
    if role_authority:
        user_id_filter = None

    # validation
    exist_project_attachment = project_attachment_service.project_attachment_repository.read_project_attachment(project_attachment_id)
    if not exist_project_attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ProjectAttachment not found")
    
    exist_project = project_service.project_repository.read_project(project_id)
    if not exist_project:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Company not exist")
    
    if user_id_filter is not None and exist_project_attachment.project.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update")

    try:
        if (image):
            await validation_file(file=image)

        content_type_image = image.content_type if image else ""
        file_extension_image = content_type_image.split('/')[1] if image else ""

        project_attachment_model = ProjectAttachment(
            id=project_attachment_id,
            project_id=project_id,
            title=title,
            is_active=is_active,
            description=description,
            website_url=website_url,
            category=category,
        )

        data = project_attachment_service.update_project_attachment(
            exist_project_attachment,
            project_attachment_model,
            exist_project,
            image,
            file_extension_image,
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


@router.delete("/{project_attachment_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def delete_project_attachment(
    project_attachment_id: str,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Delete ProjectAttachment
        
        - should login
        - allow to delete with role that has authority

        - when has authority delete other it allow delete project_attachment other
        - when no has authority, it only delete project_attachment it self
    """
    user_id_active = payload.get("uid", None)

    # service
    project_attachment_service = ProjectAttachmentService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.project.value, name=RoleAuthorityName.delete.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to delete")
    
    exist_project_attachment = project_attachment_service.project_attachment_repository.read_project_attachment(project_attachment_id)
    if not exist_project_attachment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ProjectAttachment not found")

    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.project.value, name=RoleAuthorityName.delete.value)
    if role_authority:
        user_id_filter = None
    
    if user_id_filter is not None and exist_project_attachment.project.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to delete")

    try:
        project_attachment_service.delete_project_attachment(project_attachment_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    status_code = status.HTTP_200_OK
    data = {
        'id': project_attachment_id,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response