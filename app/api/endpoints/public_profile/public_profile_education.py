from fastapi import APIRouter, Depends, Query, Request, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import LanguageOption
from app.models.response import GeneralDataPaginateResponse
from app.services.school.school_service import SchoolService
from app.services.school.school_translation_service import SchoolTranslationService
from app.services.education.education_translation_service import EducationTranslationService
from app.services.user_service import UserService
from app.utils.manual import get_total_pages

router = APIRouter()

@router.get("/{username}/{language_id}/education", response_model=GeneralDataPaginateResponse, status_code=status.HTTP_200_OK)
def public_profile_education(
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
        Profile user public education
    """
    user_service = UserService(db)
    school_service = SchoolService(db)
    school_translation_service = SchoolTranslationService(db)
    education_translation_service = EducationTranslationService(db)
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

    education_translations = education_translation_service.education_translation_repository.get_education_translation_by_user_id_and_language_id(
        user_id=user.id,
        language_id=language_id,
        offset=offset, 
        size=size, 
        sort_by=sort_by, 
        sort_order=sort_order, 
        custom_filters=custom_filters,
    )
    
    if not education_translations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")
    
    count = education_translation_service.education_translation_repository.count_education_translation_by_user_id_and_language_id(
        user_id=user.id,
        language_id=language_id,
        custom_filters=custom_filters,
    )
    total_pages = get_total_pages(size, count)

    datas = []
    for education_translation in education_translations:
        school = {}
        if education_translation.education.school:
            exist_school_translation = school_translation_service.school_translation_repository.get_school_translation_by_school_id_and_language_id(
                school_id=education_translation.education.school_id,
                language_id=language_id
            )
            image_url = f"{base_url}{school_service.static_folder_image}/{exist_school_translation.school.image_url}" if exist_school_translation.school.image_url else None
            logo_url = f"{base_url}{school_service.static_folder_logo}/{exist_school_translation.school.logo_url}" if exist_school_translation.school.logo_url else None
            website_url = str(exist_school_translation.school.website_url) if exist_school_translation.school.website_url else None
            school = {
                'name': exist_school_translation.name,
                'description': exist_school_translation.description,
                'address': exist_school_translation.address,
                'image_url': image_url,
                'logo_url': logo_url,
                'website_url': website_url,
            } if exist_school_translation else {}

        datas.append({
            'id': education_translation.id,
            'title': education_translation.title,
            'degree': education_translation.degree,
            'description': education_translation.description,
            'field_of_study': education_translation.field_of_study,
            'started_at': str(education_translation.education.started_at),
            'finished_at': str(education_translation.education.finished_at),
            'created_at': str(education_translation.created_at),
            'updated_at': str(education_translation.updated_at),
            'school': school
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

