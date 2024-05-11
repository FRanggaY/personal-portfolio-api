from datetime import date
from fastapi import APIRouter, Depends, Form, Query, Request, UploadFile, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.response import GeneralDataPaginateResponse, GeneralDataResponse
from app.models.role_authority import RoleAuthorityFeature, RoleAuthorityName
from app.models.solution.solution import Solution
from app.services.role_authority_service import RoleAuthorityService
from app.services.solution.solution_service import SolutionService
from app.services.user_service import UserService
from app.utils.authentication import Authentication
from app.utils.handling_file import validation_file
from app.utils.manual import get_total_pages

router = APIRouter()

@router.post("", response_model=GeneralDataResponse, status_code=status.HTTP_201_CREATED)
async def create_solution(
    title: str = Form(..., min_length=1, max_length=128),
    image: UploadFile = None,
    logo: UploadFile = None,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Create Solution

        - should login
        - allow to create with role that has authority
    """
    user_id_active = payload.get("uid", None)

    # service
    solution_service = SolutionService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.solution.value, name=RoleAuthorityName.create.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to create")

    try:
        if (image):
            await validation_file(file=image)
        
        if (logo):
            await validation_file(file=logo)

        content_type_image = image.content_type if image else ""
        file_extension_image = content_type_image.split('/')[1] if image else ""
        
        content_type_logo = logo.content_type if logo else ""
        file_extension_logo = content_type_logo.split('/')[1] if logo else ""
        
        solution_model = Solution(
            user_id=user_id_active,
            title=title,
        )

        file_name = f"{user_active.username}-{title}"

        data = solution_service.create_solution(
            solution=solution_model,
            image=image,
            logo=logo,
            file_extension_image=file_extension_image,
            file_extension_logo=file_extension_logo,
            file_name=file_name,
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
def read_solutions(
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
        Read All Solution

        - need login

        - when has authority create other it show solution information
        - when no has authority, it only show solution it self
    """
    user_id_active = payload.get("uid", None)
    solution_service = SolutionService(db)

    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)

    user_id_filter = user_id_active
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.solution_other.value, name=RoleAuthorityName.create.value)
    if role_authority:
        user_id_filter = None

    base_url = str(request.base_url) if request else ""
    custom_filters = {filter_by_column: filter_value} if filter_by_column and filter_value else None

    solutions = solution_service.solution_repository.read_solutions(
        offset=offset, 
        size=size, 
        sort_by=sort_by, 
        sort_order=sort_order, 
        custom_filters=custom_filters,
        is_active=is_active,
        user_id=user_id_filter,
    )

    if not solutions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")
    
    count = solution_service.solution_repository.count_solutions(
        custom_filters=custom_filters,
        is_active=is_active,
        user_id=user_id_filter,
    )
    total_pages = get_total_pages(size, count)
    

    datas = []
    for solution in solutions:
        datas.append({
            'id': solution.id,
            'title': solution.title,
            'is_active': solution.is_active,
            'created_at': str(solution.created_at),
            'updated_at': str(solution.updated_at),
            'image_url': f"{base_url}{solution_service.static_folder_image}/{solution.image_url}" if solution.image_url else None,
            'logo_url': f"{base_url}{solution_service.static_folder_logo}/{solution.logo_url}" if solution.logo_url else None,
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

@router.get("/{solution_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
def read_solution(
    solution_id: str,
    request: Request,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Read Solution

        - should login

        - when has authority view other it show solution information
        - when no has authority, it only show solution it self
    """
    user_id_active = payload.get("uid", None)
    solution_service = SolutionService(db)

    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)

    user_id_filter = user_id_active
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.solution_other.value, name=RoleAuthorityName.view.value)
    if role_authority:
        user_id_filter = None

    base_url = str(request.base_url) if request else ""
    solution = solution_service.solution_repository.read_solution(solution_id)

    if not solution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data not found")

    if user_id_filter is not None and solution.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to read")

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data={
            'id': solution.id,
            'title': solution.title,
            'is_active': solution.is_active,
            'created_at': str(solution.created_at),
            'updated_at': str(solution.updated_at),
            'image_url': f"{base_url}{solution_service.static_folder_image}/{solution.image_url}" if solution.image_url else None,
            'logo_url': f"{base_url}{solution_service.static_folder_logo}/{solution.logo_url}" if solution.logo_url else None,
        },
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.patch("/{solution_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def update_solution(
    solution_id: str,
    title: str = Form(None, min_length=0, max_length=128),
    image: UploadFile = None,
    logo: UploadFile = None,
    is_active: bool = Form(default=True),
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Update Solution
        
        - should login
        - allow to update with role that has authority

        - when has authority edit other it allow edit solution other
        - when no has authority, it only edit solution it self
    """
    user_id_active = payload.get("uid", None)

    # service
    solution_service = SolutionService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.solution.value, name=RoleAuthorityName.edit.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to edit")
    
    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.solution_other.value, name=RoleAuthorityName.edit.value)
    if role_authority:
        user_id_filter = None

    # validation
    exist_solution = solution_service.solution_repository.read_solution(solution_id)
    if not exist_solution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solution not found")
    
    if user_id_filter is not None and exist_solution.user_id != user_id_filter:
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

        solution_model = Solution(
            id=solution_id,
            title=title,
            is_active=is_active,
        )

        data = solution_service.update_solution(
            exist_solution,
            solution_model,
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


@router.delete("/{solution_id}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def delete_solution(
    solution_id: str,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        Delete Solution
        
        - should login
        - allow to delete with role that has authority

        - when has authority delete other it allow delete solution other
        - when no has authority, it only delete solution it self
    """
    user_id_active = payload.get("uid", None)

    # service
    solution_service = SolutionService(db)
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)
    
    user_active = user_service.user_repository.read_user(user_id_active)
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.solution.value, name=RoleAuthorityName.delete.value)
    if not role_authority:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allow to delete")
    
    exist_solution = solution_service.solution_repository.read_solution(solution_id)
    if not exist_solution:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solution not found")

    user_id_filter = user_id_active
    role_authority = role_authority_service.role_authority_repository.get_role_authority_by_specific(role_id=user_active.role_id, feature=RoleAuthorityFeature.solution_other.value, name=RoleAuthorityName.delete.value)
    if role_authority:
        user_id_filter = None
    
    if user_id_filter is not None and exist_solution.user_id != user_id_filter:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to delete")

    try:
        solution_service.delete_solution(solution_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    status_code = status.HTTP_200_OK
    data = {
        'id': solution_id,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response

@router.get("-resource", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def read_solution_resource(
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    """
        List access control list for resource solution based role id

        - should login
    """
    user_id_active = payload.get("uid", None)
    
    # get service
    role_authority_service = RoleAuthorityService(db)
    user_service = UserService(db)

    user_active = user_service.user_repository.read_user(user_id_active)

    # list
    role_authorities = role_authority_service.role_authority_repository.read_role_authorities(role_id=user_active.role_id, feature=[RoleAuthorityFeature.solution.value, RoleAuthorityFeature.solution_other.value])
    role_authority_list = [role_authority.name for role_authority in role_authorities] if role_authorities else []

    status_code = status.HTTP_200_OK
    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=role_authority_list,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response