from supabase import create_client, Client
from dotenv import load_dotenv
import os
import jwt
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Valida JWT de Supabase y devuelve user_id + org_id"""
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="No sub en token")

        # Schema real: memberships → org_id (NO profiles → tenant_id)
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

        # Devolvemos "tenant_id" como alias de org_id para consistencia interna
        return {"user_id": user_id, "tenant_id": org_id}

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Token inválido: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")
