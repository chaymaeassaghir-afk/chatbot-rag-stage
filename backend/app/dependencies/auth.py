from app.security.keycloak import (
    require_keycloak_user,
    require_admin,
)

get_current_user = require_keycloak_user
require_user = require_keycloak_user