from fastapi import APIRouter, Depends, Form, Query, Request, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.response import GeneralDataPaginateResponse, GeneralDataResponse
from app.models.role_authority import RoleAuthorityFeature, RoleAuthorityName
from app.models.project.project_skill import ProjectSkill
from app.services.project.project_service import ProjectService
from app.services.role_authority_service import RoleAuthorityService
from app.services.project.project_skill_service import ProjectSkillService
from app.services.skill.skill_service import SkillService
from app.services.user_service import UserService
from app.utils.authentication import Authentication
from app.utils.manual import get_total_pages

router = APIRouter()

@router.post("", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
async def create_project_skill(
    project_id: str = Form(..., min_length=1, max_length=36),
    skill_id: str = Form(..., min_length=1, max_length=36),
    is_active: bool = Form(default=True),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Create Project Skill

        - should login
        - allow to create with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    project_skill_service = ProjectSkillService(db)
    project_service = ProjectService(db)
    skill_service = SkillService(db)
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
    
    exist_skill = skill_service.skill_repository.read_skill(skill_id)
    if not exist_skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    
    exist_data = project_skill_service.project_skill_repository.get_project_skill_by_project_id_and_skill_id(project_id=project_id, skill_id=skill_id)
    if exist_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Project Skill already exist")
    
    try:
        project_skill_model = ProjectSkill(
            skill_id=skill_id,
            project_id=project_id,
            is_active=is_active,
        )

        data = project_skill_service.project_skill_repository.create_project_skill(project_skill_model)
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
def read_project_skills(
    request: Request,
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
        Read All ProjectSkill

        - need login
    """
    project_skill_service = ProjectSkillService(db)
    skill_service = SkillService(db)

    base_url = str(request.base_url) if request else ""
    custom_filters = {filter_by_column: filter_value} if filter_by_column and filter_value else None

    project_skills = project_skill_service.project_skill_repository.read_project_skills(
        offset=offset, 
        size=size, 
        sort_by=sort_by, 
        sort_order=sort_order, 
        custom_filters=custom_filters,
        is_active=is_active,
        project_id=project_id
    )

    if not project_skills:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")
    
    count = project_skill_service.project_skill_repository.count_project_skills(
        custom_filters=custom_filters,
        is_active=is_active,
        project_id=project_id
    )
    total_pages = get_total_pages(size, count)
    

    datas = []
    for project_skill in project_skills:
        image_url = f"{base_url}{skill_service.static_folder_image}/{project_skill.skill.image_url}" if project_skill.skill.image_url else None
        logo_url = f"{base_url}{skill_service.static_folder_logo}/{project_skill.skill.logo_url}" if project_skill.skill.logo_url else None
        skill = {
            'id': project_skill.skill.id,
            'name': project_skill.skill.name,
            'category': project_skill.skill.category,
            'image_url': image_url,
            'logo_url': logo_url,
        } if project_skill.skill else None
        project = {
            'id': project_skill.project.id,
            'title': project_skill.project.title,
        } if project_skill.project else None
        datas.append({
            'id': project_skill.id,
            'skill': skill,
            'project': project,
            'is_active': project_skill.is_active,
            'created_at': str(project_skill.created_at),
            'updated_at': str(project_skill.updated_at),
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

@router.patch("/{project_id}/{skill_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def update_project_skill(
    project_id: str,
    skill_id: str,
    is_active: bool = Form(default=True),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Update Project Skill
        
        - should login
        - allow to update with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    project_skill_service = ProjectSkillService(db)
    skill_service = SkillService(db)
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
    exist_skill = skill_service.skill_repository.read_skill(skill_id)
    if not exist_skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    
    exist_project_skill = project_skill_service.project_skill_repository.get_project_skill_by_project_id_and_skill_id(project_id=project_id, skill_id=skill_id)
    if not exist_project_skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project Skill not found")
    
    if user_id_filter is not None and exist_project_skill.project.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update")

    try:
        project_skill_model = ProjectSkill(
            id=exist_project_skill.id,
            project_id=project_id,
            is_active=is_active,
        )

        data = project_skill_service.update_project_skill(
            exist_project_skill,
            project_skill_model,
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


@router.delete("/{project_id}/{skill_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def delete_project_skill(
    project_id: str,
    skill_id: str,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Delete ProjectSkill
        
        - should login
        - allow to delete with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    project_skill_service = ProjectSkillService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.project.value, name=RoleAuthorityName.delete.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to delete")

    exist_project_skill = project_skill_service.project_skill_repository.get_project_skill_by_project_id_and_skill_id(project_id, skill_id)
    if not exist_project_skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.project_other.value, name=RoleAuthorityName.delete.value)
    if role_authority:
        user_id_filter = None

    if user_id_filter is not None and exist_project_skill.project.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to delete")

    try:
        project_skill_service.project_skill_repository.delete_project_skill(exist_project_skill)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    status_code = status.HTTP_200_OK
    data = {
        'project_id': project_id,
        'skill_id': skill_id,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response