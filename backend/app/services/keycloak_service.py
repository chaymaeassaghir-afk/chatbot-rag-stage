import requests
import jwt

from jwt import PyJWKClient

from app.config_keycloak import (
    JWKS_URL,
    ISSUER
)


class KeycloakService:

    jwk_client = PyJWKClient(JWKS_URL)

    @staticmethod
    def verify_token(token: str):

        signing_key = KeycloakService.jwk_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            issuer=ISSUER,
            options={
                "verify_aud": False
            }
        )

        return payload