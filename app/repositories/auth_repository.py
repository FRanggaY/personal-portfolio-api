import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.generate_access_token import generate_access_token
from app.utils.generate_refresh_token import generate_refresh_token

class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def auth_login(self, user: User, is_password_valid: bool):
        if is_password_valid:
            # add payload
            payload = {
                'uid': user.id,
                'username': user.username,
                'role_code': user.role.code if user.role else "",
            }
            # generate refresh_token
            refresh_token = generate_refresh_token(payload)
            # generate access token and access token expired
            access_token, access_token_expired_at = generate_access_token(payload)

            # saving data of refresh token
            ## COMING SOON

            # update last login
            user.last_login_at = sa.func.now()
            self.db.commit()

            return {
                'user_id': user.id,
                'access_token': access_token,
                'refresh_token': refresh_token,
                'access_token_expired_at': access_token_expired_at,
            }

        else:
            raise ValueError("Password invalid")
