from fastapi import APIRouter, Depends, Query, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import LanguageOption
from app.models.response import GeneralDataPaginateResponse
from app.services.company.company_service import CompanyService
from app.services.company.company_translation_service import CompanyTranslationService
from app.services.experience.experience_translation_service import ExperienceTranslationService
from app.services.user_service import UserService
from app.utils.manual import get_total_pages

router = APIRouter()

@router.get("/{username}/{language_id}/experience", response_model=GeneralDataPaginateResponse, status_code=status.HTTP_200_OK)
def public_profile_experience(
    username: str, 
    language_id: LanguageOption,
    offset: int = Query(1, ge=1), 
    size: int = Query(10, ge=1, lt=100),
    sort_by: str = Query(None),
    sort_order: str = Query(None),
    filter_by_column: str = Query(None),
    filter_value: str = Query(None),
    db: Session = Depends(get_db)
):
    """
        Profile user public experience
    """
    user_service = UserService(db)
    company_service = CompanyService(db)
    company_translation_service = CompanyTranslationService(db)
    experience_translation_service = ExperienceTranslationService(db)
    custom_filters = {filter_by_column: filter_value} if filter_by_column and filter_value else None

    try:
        user = user_service.user_repository.get_user_by_username(username)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='this user is not active')
    
    language_id = language_id.value

    experience_translations = experience_translation_service.experience_translation_repository.get_experience_translation_by_user_id_and_language_id(
        user_id=user.id,
        language_id=language_id,
        offset=offset, 
        size=size, 
        sort_by=sort_by, 
        sort_order=sort_order, 
        custom_filters=custom_filters,
    )
    
    if not experience_translations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")
    
    count = experience_translation_service.experience_translation_repository.count_experience_translation_by_user_id_and_language_id(
        user_id=user.id,
        language_id=language_id,
        custom_filters=custom_filters,
    )
    total_pages = get_total_pages(size, count)

    datas = []
    for experience_translation in experience_translations:
        company = {}
        if experience_translation.experience.company:
            exist_company_translation = company_translation_service.company_translation_repository.get_company_translation_by_company_id_and_language_id(
                company_id=experience_translation.experience.company_id,
                language_id=language_id
            )
            image_url = f"{company_service.static_folder_image}/{exist_company_translation.company.image_url}" if exist_company_translation.company.image_url else None
            logo_url = f"{company_service.static_folder_logo}/{exist_company_translation.company.logo_url}" if exist_company_translation.company.logo_url else None
            website_url = str(exist_company_translation.company.website_url) if exist_company_translation.company.website_url else None
            company = {
                'name': exist_company_translation.name,
                'description': exist_company_translation.description,
                'address': exist_company_translation.address,
                'image_url': image_url,
                'logo_url': logo_url,
                'website_url': website_url,
            } if exist_company_translation else {}

        datas.append({
            'id': experience_translation.id,
            'title': experience_translation.title,
            'description': experience_translation.description,
            'employee_type': experience_translation.employee_type,
            'location': experience_translation.location,
            'location_type': experience_translation.location_type,
            'started_at': str(experience_translation.experience.started_at),
            'finished_at': str(experience_translation.experience.finished_at) if experience_translation.experience.finished_at else None,
            'created_at': str(experience_translation.created_at),
            'updated_at': str(experience_translation.updated_at),
            'company': company
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

