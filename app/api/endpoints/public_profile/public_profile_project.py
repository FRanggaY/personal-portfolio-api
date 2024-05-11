from fastapi import APIRouter, Depends, Query, Request, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import LanguageOption
from app.models.response import GeneralDataPaginateResponse, GeneralDataResponse
from app.services.project.project_attachment_service import ProjectAttachmentService
from app.services.project.project_service import ProjectService
from app.services.project.project_skill_service import ProjectSkillService
from app.services.project.project_translation_service import ProjectTranslationService
from app.services.skill.skill_service import SkillService
from app.services.user_service import UserService
from app.utils.manual import get_total_pages

router = APIRouter()

@router.get("/{username}/{language_id}/project", response_model=GeneralDataPaginateResponse, status_code=status.HTTP_200_OK)
def public_profile_project(
    username: str, 
    language_id: LanguageOption,
    request: Request, 
    offset: int = Query(1, ge=1), 
    size: int = Query(10, ge=1, lt=100),
    sort_by: str = Query(None),
    sort_order: str = Query(None),
    filter_by_column: str = Query(None),
    filter_value: str = Query(None),
    db: Session = Depends(get_db)
):
    """
        Profile user public project
    """
    user_service = UserService(db)
    project_service = ProjectService(db)
    project_translation_service = ProjectTranslationService(db)
    custom_filters = {filter_by_column: filter_value} if filter_by_column and filter_value else None

    base_url = str(request.base_url) if request else ""

    try:
        user = user_service.user_repository.get_user_by_username(username)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='this user is not active')
    
    language_id = language_id.value

    project_translations = project_translation_service.project_translation_repository.get_project_translation_by_user_id_and_language_id(
        user_id=user.id,
        language_id=language_id,
        offset=offset, 
        size=size, 
        sort_by=sort_by, 
        sort_order=sort_order, 
        custom_filters=custom_filters,
    )
    
    if not project_translations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")
    
    count = project_translation_service.project_translation_repository.count_project_translation_by_user_id_and_language_id(
        user_id=user.id,
        language_id=language_id,
        custom_filters=custom_filters,
    )
    total_pages = get_total_pages(size, count)

    datas = []
    for project_translation in project_translations:
        image_url = f"{base_url}{project_service.static_folder_image}/{project_translation.project.image_url}" if project_translation.project.image_url else None
        logo_url = f"{base_url}{project_service.static_folder_logo}/{project_translation.project.logo_url}" if project_translation.project.logo_url else None
        
        datas.append({
            'id': project_translation.id,
            'title': project_translation.title,
            'description': project_translation.description,
            'slug': project_translation.project.slug,
            'created_at': str(project_translation.created_at),
            'updated_at': str(project_translation.updated_at),
            'image_url': image_url,
            'logo_url': logo_url    
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


@router.get("/{username}/{language_id}/project/{project_slug}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
def public_profile_project_detail(
    username: str, 
    language_id: LanguageOption, 
    project_slug: str, 
    request: Request, 
    db: Session = Depends(get_db)
):
    """
        Profile user public project detail
    """
    user_service = UserService(db)
    project_service = ProjectService(db)
    project_translation_service = ProjectTranslationService(db)
    project_skill_service = ProjectSkillService(db)
    skill_service = SkillService(db)
    project_attachment_service = ProjectAttachmentService(db)

    base_url = str(request.base_url) if request else ""

    try:
        user = user_service.user_repository.get_user_by_username(username)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='this user is not active')
    
    project = project_service.project_repository.get_project_by_user_id_and_slug(user.id, project_slug)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

    language_id = language_id.value

    project_translation = project_translation_service.project_translation_repository.get_project_translation_by_project_id_and_language_id(
        project_id=project.id,
        language_id=language_id,
    )
    
    if not project_translation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")
    
    skill_translations = project_skill_service.project_skill_repository.get_project_skill_by_project_id_and_language_id(
        project_id=project.id,
        language_id=language_id,
    )

    skills = []
    if skill_translations:
        for skill_translation in skill_translations:
            skills.append({
                'id': skill_translation.id,
                'name': skill_translation.name,
                'description': skill_translation.description,
                'created_at': str(skill_translation.created_at),
                'updated_at': str(skill_translation.updated_at),
                'image_url': f"{base_url}{skill_service.static_folder_image}/{skill_translation.skill.image_url}" if skill_translation.skill.image_url else None,
                'logo_url': f"{base_url}{skill_service.static_folder_logo}/{skill_translation.skill.logo_url}" if skill_translation.skill.logo_url else None,
                'website_url': str(skill_translation.skill.website_url) if skill_translation.skill.website_url else None,
            })

    project_attachments = project_attachment_service.project_attachment_repository.read_project_attachments(
        project_id=project.id,
        is_active=True
    )

    attachments = []
    if project_attachments:
        for project_attachment in project_attachments:
            attachments.append({
               'id': project_attachment.id,
                'title': project_attachment.title,
                'is_active': project_attachment.is_active,
                'description': project_attachment.description if project_attachment.description else None,
                'website_url': project_attachment.website_url if project_attachment.website_url else None,
                'category': project_attachment.category,
                'created_at': str(project_attachment.created_at),
                'updated_at': str(project_attachment.updated_at),
                'image_url': f"{base_url}{project_attachment_service.static_folder_image}/{project_attachment.image_url}" if project_attachment.image_url else None,
            })


    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data={
            'id': project_translation.id,
            'title': project_translation.title,
            'description': project_translation.description,
            'is_active': project_translation.project.is_active,
            'created_at': str(project.created_at),
            'updated_at': str(project.updated_at),
            'image_url': f"{base_url}{project_service.static_folder_image}/{project.image_url}" if project.image_url else None,
            'logo_url': f"{base_url}{project_service.static_folder_logo}/{project.logo_url}" if project.logo_url else None,
            'skills': skills,
            'attachments': attachments,
        },
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

