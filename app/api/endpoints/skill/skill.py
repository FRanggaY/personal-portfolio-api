from fastapi import APIRouter, Depends, Form, Query, Request, UploadFile, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.response import GeneralDataPaginateResponse, GeneralDataResponse
from app.models.role_authority import RoleAuthorityFeature, RoleAuthorityName
from app.models.skill.skill import Skill
from app.services.role_authority_service import RoleAuthorityService
from app.services.role_service import RoleService
from app.services.skill.skill_service import SkillService
from app.services.user_service import UserService
from app.utils.authentication import Authentication
from app.utils.handling_file import validation_file
from app.utils.manual import get_total_pages

router = APIRouter()

@router.post("", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
async def create_skill(
    code: str = Form(..., min_length=1, max_length=36),
    name: str = Form(..., min_length=1, max_length=36),
    website_url: str = Form(None, min_length=0, max_length=512),
    category: str = Form(None, min_length=0, max_length=512),
    image: UploadFile = None,
    logo: UploadFile = None,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Create Skill

        - should login
        - allow to create with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    skill_service = SkillService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.skill_other.value, name=RoleAuthorityName.create.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to create")

    # validation
    exist_code = skill_service.skill_repository.get_skill_by_code(code)
    if exist_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code already exist")
    
    exist_name = skill_service.skill_repository.get_skill_by_name(name)
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

        skill_model = Skill(
            code=code,
            name=name,
            website_url=website_url,
            category=category
        )

        data = skill_service.create_skill(
            skill_model,
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
def read_skills(
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
        Read All Skill

        - need login
    """
    skill_service = SkillService(db)

    base_url = str(request.base_url) if request else ""
    custom_filters = {filter_by_column: filter_value} if filter_by_column and filter_value else None

    skills = skill_service.skill_repository.read_skills(
        offset=offset, 
        size=size, 
        sort_by=sort_by, 
        sort_order=sort_order, 
        custom_filters=custom_filters,
        is_active=is_active
    )

    if not skills:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")
    
    count = skill_service.skill_repository.count_skills(
        custom_filters=custom_filters,
        is_active=is_active
    )
    total_pages = get_total_pages(size, count)
    

    datas = []
    for skill in skills:
        datas.append({
            'id': skill.id,
            'name': skill.name,
            'code': skill.code,
            'is_active': skill.is_active,
            'category': skill.category,
            'created_at': str(skill.created_at),
            'updated_at': str(skill.updated_at),
            'image_url': f"{base_url}{skill_service.static_folder_image}/{skill.image_url}" if skill.image_url else None,
            'logo_url': f"{base_url}{skill_service.static_folder_logo}/{skill.logo_url}" if skill.logo_url else None,
            'website_url': str(skill.website_url) if skill.website_url else None,
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

@router.get("/{skill_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
def read_skill(
    skill_id: str,
    request: Request,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read Skill

        - should login
    """
    skill_service = SkillService(db)
    base_url = str(request.base_url) if request else ""
    skill = skill_service.skill_repository.read_skill(skill_id)

    if not skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data={
            'id': skill.id,
            'name': skill.name,
            'code': skill.code,
            'is_active': skill.is_active,
            'category': skill.category,
            'created_at': str(skill.created_at),
            'updated_at': str(skill.updated_at),
            'image_url': f"{base_url}{skill_service.static_folder_image}/{skill.image_url}" if skill.image_url else None,
            'logo_url': f"{base_url}{skill_service.static_folder_logo}/{skill.logo_url}" if skill.logo_url else None,
            'website_url': str(skill.website_url) if skill.website_url else None,
        },
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.patch("/{skill_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def update_skill(
    skill_id: str,
    code: str = Form(None, min_length=0, max_length=36),
    name: str = Form(None, min_length=0, max_length=36),
    website_url: str = Form(None, min_length=0, max_length=256),
    category: str = Form(None, min_length=0, max_length=256),
    is_active: bool = Form(default=True),
    image: UploadFile = None,
    logo: UploadFile = None,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Update Skill
        
        - should login
        - allow to update with role that has authority
    """
    user_id_active = payload.get("uid", None)
    
    # service
    skill_service = SkillService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.skill_other.value, name=RoleAuthorityName.edit.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to edit")
    
    # validation
    exist_skill = skill_service.skill_repository.read_skill(skill_id)
    if not exist_skill:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Skill not found")
    
    try:
        if (image):
            await validation_file(file=image)
        
        if (logo):
            await validation_file(file=logo)

        content_type_image = image.content_type if image else ""
        file_extension_image = content_type_image.split('/')[1] if image else ""
        
        content_type_logo = logo.content_type if logo else ""
        file_extension_logo = content_type_logo.split('/')[1] if logo else ""

        skill_model = Skill(
            id=skill_id,
            code=code,
            name=name,
            website_url=website_url,
            category=category,
            is_active=is_active,
        )

        data = skill_service.update_skill(
            exist_skill,
            skill_model,
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


@router.delete("/{skill_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def delete_skill(
    skill_id: str,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Delete Skill
        
        - should login
        - allow to delete with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    skill_service = SkillService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.skill_other.value, name=RoleAuthorityName.delete.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to delete")

    try:
        skill_service.delete_skill(skill_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    status_code = status.HTTP_200_OK
    data = {
        'id': skill_id,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.get("-resource", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def read_skill_resource(
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        List access control list for resource skill based role id

        - should login
    """
    user_id_active = payload.get("uid", None)
    
    # get service
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)

    user_active = user_service.user_repository.read_user(user_id_active)

    # list
    role_authorities = role_authority_service.role_authority_repository.read_role_authorities(role_id=user_active.role_id, feature=[RoleAuthorityFeature.skill_other.value, RoleAuthorityFeature.skill_mapping.value, RoleAuthorityFeature.skill.value])
    role_authority_list = [f"{role_authority.name}_{role_authority.feature}" for role_authority in role_authorities] if role_authorities else []

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=role_authority_list,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response