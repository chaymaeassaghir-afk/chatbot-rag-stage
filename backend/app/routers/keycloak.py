from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.keycloak_service import KeycloakService

security = HTTPBearer()

router = APIRouter(
    prefix="/keycloak",
    tags=["Keycloak"]
)

@router.get("/verify")
def verify(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):

    payload = KeycloakService.verify_token(
        credentials.credentials
    )

    return payload