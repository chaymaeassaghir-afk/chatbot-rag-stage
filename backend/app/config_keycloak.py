KEYCLOAK_SERVER = "http://localhost:8081"

REALM = "rag-stage"

CLIENT_ID = "fastapi"

CLIENT_SECRET = "7DXMBNzbsAhf2UGelxw4TDW6H5zdWqVB"

ISSUER = f"{KEYCLOAK_SERVER}/realms/{REALM}"

JWKS_URL = f"{ISSUER}/protocol/openid-connect/certs"