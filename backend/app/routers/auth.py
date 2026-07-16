from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db

from app.schemas.user import UserCreate
from app.schemas.user import UserResponse

from app.services.user_service import UserService
from app.schemas.user import UserLogin
from app.schemas.user import Token
from fastapi import HTTPException
from app.dependencies.auth import require_keycloak_user

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register", response_model=UserResponse)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    return UserService.create_user(
        db,
        user.username,
        user.email,
        user.password
    )


@router.post("/login", response_model=Token)
def login(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):

    user = UserService.authenticate(
        db=db,
        username=credentials.username,
        password=credentials.password
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Nom d'utilisateur ou mot de passe incorrect"
        )

    token = JWTService.create_access_token(
        username=user.username,
        role=user.role
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }





@router.get("/users", response_model=list[UserResponse])
def users(
    db: Session = Depends(get_db)
):

    return UserService.list_users(db)


@router.get("/me")
def me(user=Depends(require_keycloak_user)):

    return user


