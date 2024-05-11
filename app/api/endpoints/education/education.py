from datetime import date
from fastapi import APIRouter, Depends, Form, Query, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.response import GeneralDataPaginateResponse, GeneralDataResponse
from app.models.role_authority import RoleAuthorityFeature, RoleAuthorityName
from app.models.education.education import Education
from app.services.role_authority_service import RoleAuthorityService
from app.services.education.education_service import EducationService
from app.services.school.school_service import SchoolService
from app.services.user_service import UserService
from app.utils.authentication import Authentication
from app.utils.manual import get_total_pages

router = APIRouter()

@router.post("", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
async def create_education(
    school_id: str = Form(..., min_length=1, max_length=36),
    title: str = Form(..., min_length=1, max_length=128),
    started_at: date = Form(...),
    finished_at: date = Form(None),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Create Education

        - should login
        - allow to create with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    school_service = SchoolService(db)
    education_service = EducationService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.education.value, name=RoleAuthorityName.create.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to create")

    # validation
    exist_school = school_service.school_repository.read_school(school_id)
    if not exist_school:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="School not exist")
    
    try:
        education_model = Education(
            school_id=school_id,
            user_id=user_id_active,
            title=title,
            started_at=started_at,
            finished_at=finished_at,
        )

        data = education_service.education_repository.create_education(
            education_model,
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
def read_educations(
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
        Read All Education

        - need login

        - when has authority create other it show education information
        - when no has authority, it only show education it self
    """
    user_id_active = payload.get("uid", None)
    education_service = EducationService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)

    user_id_filter = user_id_active
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.education_other.value, name=RoleAuthorityName.create.value)
    if role_authority:
        user_id_filter = None

    custom_filters = {filter_by_column: filter_value} if filter_by_column and filter_value else None

    educations = education_service.education_repository.read_educations(
        offset=offset, 
        size=size, 
        sort_by=sort_by, 
        sort_order=sort_order, 
        custom_filters=custom_filters,
        is_active=is_active,
        user_id=user_id_filter,
    )

    if not educations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")
    
    count = education_service.education_repository.count_educations(
        custom_filters=custom_filters,
        is_active=is_active,
        user_id=user_id_filter,
    )
    total_pages = get_total_pages(size, count)
    

    datas = []
    for education in educations:
        school = {
            'id': education.school.id,
            'name': education.school.name,
        } if education.school else None
        datas.append({
            'id': education.id,
            'school': school,
            'title': education.title,
            'is_active': education.is_active,
            'started_at': str(education.started_at),
            'finished_at': str(education.finished_at) if education.finished_at else None,
            'created_at': str(education.created_at),
            'updated_at': str(education.updated_at),
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

@router.get("/{education_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
def read_education(
    education_id: str,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read Education

        - should login

        - when has authority view other it show education information
        - when no has authority, it only show education it self
    """
    user_id_active = payload.get("uid", None)
    education_service = EducationService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)

    user_id_filter = user_id_active
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.education_other.value, name=RoleAuthorityName.view.value)
    if role_authority:
        user_id_filter = None

    education = education_service.education_repository.read_education(education_id)

    if not education:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

    if user_id_filter is not None and education.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to read")
   
    school = {
        'id': education.school.id,
        'name': education.school.name,
    } if education.school else None

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data={
            'id': education.id,
            'school': school,
            'title': education.title,
            'is_active': education.is_active,
            'started_at': str(education.started_at),
            'finished_at': str(education.finished_at) if education.finished_at else None,
            'created_at': str(education.created_at),
            'updated_at': str(education.updated_at),
        },
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.patch("/{education_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def update_education(
    education_id: str,
    school_id: str = Form(..., min_length=1, max_length=36),
    title: str = Form(None, min_length=0, max_length=128),
    started_at: date = Form(None),
    finished_at: date = Form(None),
    is_active: bool = Form(default=True),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Update Education
        
        - should login
        - allow to update with role that has authority

        - when has authority edit other it allow edit education other
        - when no has authority, it only edit education it self
    """
    user_id_active = payload.get("uid", None)

    # service
    school_service = SchoolService(db)
    education_service = EducationService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.education.value, name=RoleAuthorityName.edit.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to edit")
    
    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.education_other.value, name=RoleAuthorityName.edit.value)
    if role_authority:
        user_id_filter = None
    
    # validation
    exist_education = education_service.education_repository.read_education(education_id)
    if not exist_education:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education not found")
    
    exist_school = school_service.school_repository.read_school(school_id)
    if not exist_school:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="School not exist")
    
    if user_id_filter is not None and exist_education.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to update")

    try:
        education_model = Education(
            id=education_id,
            school_id=school_id,
            title=title,
            started_at=started_at,
            finished_at=finished_at,
            is_active=is_active,
        )

        data = education_service.update_education(
            exist_education,
            education_model,
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


@router.delete("/{education_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def delete_education(
    education_id: str,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Delete Education
        
        - should login
        - allow to delete with role that has authority

        - when has authority delete other it allow delete education other
        - when no has authority, it only delete education it self
    """
    user_id_active = payload.get("uid", None)

    # service
    education_service = EducationService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.education.value, name=RoleAuthorityName.delete.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to delete")
    
    exist_education = education_service.education_repository.read_education(education_id)
    if not exist_education:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Education not found")
    
    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.education_other.value, name=RoleAuthorityName.delete.value)
    if role_authority:
        user_id_filter = None
    
    if user_id_filter is not None and exist_education.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to delete")

    try:
        education_service.education_repository.delete_education(exist_education)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    status_code = status.HTTP_200_OK
    data = {
        'id': education_id,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.get("-resource", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def read_education_resource(
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        List access control list for resource education based role id

        - should login
    """
    user_id_active = payload.get("uid", None)
    
    # get service
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)

    user_active = user_service.user_repository.read_user(user_id_active)

    # list
    role_authorities = role_authority_service.role_authority_repository.read_role_authorities(role_id=user_active.role_id, feature=[RoleAuthorityFeature.education.value, RoleAuthorityFeature.education_other.value])
    role_authority_list = [role_authority.name for role_authority in role_authorities] if role_authorities else []

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=role_authority_list,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response