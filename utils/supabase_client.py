from supabase import create_client, Client
from dotenv import load_dotenv
import os
import jwt
from jwt import PyJWKClient
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

security = HTTPBearer()

# Cliente JWKS con cache automático (PyJWT nativo)
_jwks_client = None


def get_jwks_client():
    global _jwks_client
    if _jwks_client is None:
        jwks_url = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
        _jwks_client = PyJWKClient(jwks_url, cache_keys=True)
    return _jwks_client


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Valida JWT de Supabase (ES256/HS256) y devuelve user_id + org_id"""
    token = credentials.credentials
    try:
        client = get_jwks_client()
        signing_key = client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256", "HS256"],
            audience="authenticated"
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="No sub en token")

        # Schema real: memberships → org_id
        membership = supabase.table("memberships") \
            .select("org_id") \
            .eq("user_id", user_id) \
            .limit(1) \
            .execute()

        if not membership.data:
            raise HTTPException(status_code=403, detail="Usuario sin membresía activa")

        org_id = membership.data[0].get("org_id")
        if not org_id:
            raise HTTPException(status_code=403, detail="No org_id encontrado")

        return {"user_id": user_id, "tenant_id": org_id}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
