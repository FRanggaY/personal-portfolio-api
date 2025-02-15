from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.response import GeneralDataResponse
from app.services.user_service import UserService

router = APIRouter()

@router.get("/{username}", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
def public_profile(username: str, db: Session = Depends(get_db)):
    """
        Profile user public
    """
    user_service = UserService(db)

    try:
        user = user_service.user_repository.get_user_by_username(username)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='this user is not active')

    status_code = status.HTTP_200_OK

    data = {
        'id': user.id,
        'username': user.username,
        'gender': user.gender,
        'name': user.name,
        'image_url': f"{user_service.static_folder_image}/{user.image_url}" if user.image_url else None,
    }

    data_response = GeneralDataResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=data_response.model_dump(), status_code=status_code)
    return response
