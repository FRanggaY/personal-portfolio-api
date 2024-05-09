from fastapi import APIRouter, Depends, Query, Request, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import LanguageOption
from app.models.response import GeneralDataPaginateResponse
from app.services.solution.solution_service import SolutionService
from app.services.solution.solution_translation_service import SolutionTranslationService
from app.services.user_service import UserService
from app.utils.manual import get_total_pages

router = APIRouter()

@router.get("/{username}/{language_id}/solution", response_model=GeneralDataPaginateResponse, status_code=status.HTTP_200_OK)
def public_profile_solution(
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
        Profile user public solution
    """
    user_service = UserService(db)
    solution_service = SolutionService(db)
    solution_translation_service = SolutionTranslationService(db)
    custom_filters = {filter_by_column: filter_value} if filter_by_column and filter_value else None

    base_url = str(request.base_url) if request else ""

    try:
        user = user_service.user_repository.get_user_by_username(username)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='this user is not active')
    
    language_id = language_id.value

    solution_translations = solution_translation_service.solution_translation_repository.get_solution_translation_by_user_id_and_language_id(
        user_id=user.id,
        language_id=language_id,
        offset=offset, 
        size=size, 
        sort_by=sort_by, 
        sort_order=sort_order, 
        custom_filters=custom_filters,
    )
    
    if not solution_translations:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")
    
    count = solution_translation_service.solution_translation_repository.count_solution_translation_by_user_id_and_language_id(
        user_id=user.id,
        language_id=language_id,
        custom_filters=custom_filters,
    )
    total_pages = get_total_pages(size, count)

    datas = []
    for solution_translation in solution_translations:
        image_url = f"{base_url}{solution_service.static_folder_image}/{solution_translation.solution.image_url}" if solution_translation.solution.image_url else None
        logo_url = f"{base_url}{solution_service.static_folder_logo}/{solution_translation.solution.logo_url}" if solution_translation.solution.logo_url else None
        
        datas.append({
            'id': solution_translation.id,
            'title': solution_translation.title,
            'description': solution_translation.description,
            'created_at': str(solution_translation.created_at),
            'updated_at': str(solution_translation.updated_at),
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

