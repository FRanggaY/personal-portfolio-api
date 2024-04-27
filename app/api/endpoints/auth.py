from fastapi import APIRouter, Depends, Form, Request, UploadFile, status, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.dtos.auth import AuthLogin, AuthProfilePassword
from app.models.response import AuthResponse, GeneralDataResponse
from app.models.user import User, UserGender
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.utils.authentication import Authentication
from app.utils.handling_file import validation_file

router = APIRouter()

@router.post("/login", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def auth_login(auth_login: AuthLogin, db: Session = Depends(get_db)):
    """
        Login user
        - check username exist
        - check password correction
    """
    auth_service = AuthService(db)

    try:
        user = auth_service.auth_login(auth_login)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))

    user_id = user.get('user_id', None)
    access_token = user.get('access_token', None)
    refresh_token = user.get('refresh_token', None)
    expired_at = user.get('access_token_expired_at', None)
    status_code = status.HTTP_200_OK

    auth_response = AuthResponse(
        code=status_code,
        status="OK",
        data={
            'id': user_id,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expired_at': expired_at
        },
    )
    response = JSONResponse(content=auth_response.model_dump(), status_code=status_code)
    response.set_cookie("access_token", access_token, max_age=expired_at * 60)
    return response

@router.get("/profile", response_model=AuthResponse, status_code=status.HTTP_200_OK)
def auth_profile(request: Request, db: Session = Depends(get_db),  payload = Depends(Authentication())):
    """
        Profile user
    """
    user_id = payload.get("uid", None)
    user_service = UserService(db)
    base_url = str(request.base_url) if request else ""

    try:
        user = user_service.user_repository.read_user(user_id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))
    
    status_code = status.HTTP_200_OK

    role_data = {
        'id': user.role.id,
        'code': user.role.code,
        'name': user.role.name,
    } if user.role else {}

    data = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'no_handphone': user.no_handphone,
        'gender': user.gender,
        'name': user.name,
        'role': role_data,
        'image_url': f"{base_url}{user_service.static_folder_image}/{user.image_url}" if user.image_url else None,
    }

    auth_response = AuthResponse(
        code=status_code,
        status="OK",
        data=data,
    )
    response = JSONResponse(content=auth_response.model_dump(), status_code=status_code)
    return response

@router.patch("/profile", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def auth_update_profile(
    username: str = Form(None, min_length=0, max_length=36),
    email: str = Form(None, min_length=0, max_length=36),
    name: str = Form(None, min_length=0, max_length=36),
    no_handphone: str = Form(None, min_length=0, max_length=256),
    gender: UserGender = Form(...),
    image: UploadFile = None,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    # get service
    user_id = payload.get("uid", None)
    user_service = UserService(db)
    
    exist_user = user_service.user_repository.read_user(user_id)
    if not exist_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    try:
        if (image):
            await validation_file(file=image)

        content_type = image.content_type if image else ""
        file_extension = content_type.split('/')[1] if image else ""

        role_id = exist_user.role_id
        is_active = exist_user.is_active

        user_model = User(
            id=user_id,
            role_id=role_id,
            username=username,
            email=email,
            name=name,
            no_handphone=no_handphone,
            gender=gender.value,
            is_active=is_active,
        )

        data = user_service.update_user(
            exist_user,
            user_model,
            image,
            file_extension,
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

@router.put("/profile/password", response_model=GeneralDataResponse, status_code=status.HTTP_200_OK)
async def auth_update_profile(
    auth_profile_password: AuthProfilePassword,
    db: Session = Depends(get_db), 
    payload = Depends(Authentication())
):
    # get service
    user_id = payload.get("uid", None)
    user_service = UserService(db)
    
    exist_user = user_service.user_repository.read_user(user_id)
    if not exist_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    is_password_valid = user_service.verify_password(auth_profile_password.old_password, exist_user.password)
    if not is_password_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is not valid")
    
    if auth_profile_password.confirm_new_password != auth_profile_password.new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New password and confirm new password are not the same")
    
    new_password = user_service.get_password_hash(auth_profile_password.new_password),
    
    user_model = User(
        id=user_id,
        password=new_password,
    )
    try:
        data = user_service.update_user_password(
            exist_user,
            user_model,
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

# @router.post("/refresh-token", response_model=AuthResponse, status_code=status.HTTP_200_OK)
# def auth_refresh_token(db: Session = Depends(get_db)):
#     """
#         Refresh token user

#         COMING SOON
#     """
#     pass

# @router.post("/logout", response_model=AuthResponse, status_code=status.HTTP_200_OK)
# def auth_logout(db: Session = Depends(get_db)):
#     """
#         Logout user

#         COMING SOON
#         - refer with saving refresh token
#     """
#     pass


