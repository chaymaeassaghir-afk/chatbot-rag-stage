import requests
from functools import lru_cache


class KeycloakService:

    def __init__(self):

        self.server = "http://localhost:8080"
        self.realm = "rag-stage"

    @property
    def realm_url(self):

        return f"{self.server}/realms/{self.realm}"

    @lru_cache(maxsize=1)
    def get_openid_configuration(self):

        url = f"{self.realm_url}/.well-known/openid-configuration"

        response = requests.get(url)

        response.raise_for_status()

        return response.json()

    @lru_cache(maxsize=1)
    def get_public_keys(self):

        config = self.get_openid_configuration()

        response = requests.get(config["jwks_uri"])

        response.raise_for_status()

        return response.json()