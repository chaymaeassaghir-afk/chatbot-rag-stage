from datetime import datetime, timedelta
from jose import jwt
from app.config_security import (
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from jose import jwt, JWTError

class JWTService:

    @staticmethod
    def create_access_token(username: str,role: str):

        expire = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )

        payload = {
            "sub": username,
            "role": role,
            "exp": expire
        }

        return jwt.encode(
            payload,
            SECRET_KEY,
            algorithm=ALGORITHM
        )

    @staticmethod
    def decode_access_token(token: str):

        try:

            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM]
            )

            return payload

        except JWTError:

            raise Exception("Token invalide") 
