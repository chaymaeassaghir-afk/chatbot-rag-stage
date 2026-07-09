from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.jwt_service import JWTService

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    token = credentials.credentials

    try:

        payload = JWTService.decode_access_token(token)

        return {
            "username": payload["sub"],
            "role": payload["role"]
        }

    except Exception:

        raise HTTPException(
            status_code=401,
            detail="Token invalide"
        )


def require_admin(
    current_user=Depends(get_current_user)
):

    if current_user["role"] != "ADMIN":

        raise HTTPException(
            status_code=403,
            detail="Accès réservé aux administrateurs."
        )

    return current_user


def require_user(
    current_user=Depends(get_current_user)
):

    return current_user