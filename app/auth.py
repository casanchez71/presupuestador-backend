from __future__ import annotations

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import PyJWKClient

from app.config import get_settings
from app.db import get_auth_db

security = HTTPBearer()

_jwks_client: PyJWKClient | None = None


def _get_jwks_client() -> PyJWKClient:
    global _jwks_client
    if _jwks_client is None:
        settings = get_settings()
        url = f"{settings.auth_url}/auth/v1/.well-known/jwks.json"
        _jwks_client = PyJWKClient(url, cache_keys=True)
    return _jwks_client


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Validate Supabase JWT via auth DB and return {user_id, org_id}."""
    token = credentials.credentials
    try:
        signing_key = _get_jwks_client().get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "HS256"],
            audience="authenticated",
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(401, "Token sin sub")

        # Auth DB (EOS) — resolve org_id from memberships
        auth_db = get_auth_db()
        membership = (
            auth_db.table("memberships")
            .select("org_id")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
        )
        if not membership.data:
            raise HTTPException(403, "Usuario sin membresia activa")

        org_id = membership.data[0].get("org_id")
        if not org_id:
            raise HTTPException(403, "Sin org_id")

        return {"user_id": user_id, "org_id": org_id}

    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expirado")
    except jwt.InvalidTokenError as e:
        raise HTTPException(401, f"Token invalido: {e}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"Error de autenticacion: {e}")
