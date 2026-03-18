from supabase import create_client, Client
from dotenv import load_dotenv
import os
import httpx
from jose import jwt, JWTError
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

security = HTTPBearer()

# Cache de JWKS para no fetchear en cada request
_jwks_cache = None


def get_jwks():
    """Obtiene las claves públicas de Supabase (con cache en memoria)"""
    global _jwks_cache
    if _jwks_cache is None:
        jwks_url = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
        response = httpx.get(jwks_url, timeout=10)
        response.raise_for_status()
        _jwks_cache = response.json()
    return _jwks_cache


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Valida JWT de Supabase (ES256 + HS256) y devuelve user_id + org_id"""
    token = credentials.credentials
    try:
        # Soporta tanto ECC (ES256, actual) como legacy HS256
        jwks = get_jwks()
        payload = jwt.decode(
            token,
            jwks,
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

    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
