"""Dual Supabase clients — Modelo C.

Auth client: connects to EOS Supabase (auth.users, memberships, organizations).
Data client: connects to Presupuestador Supabase (budgets, items, catalogs, etc.).

If AUTH_SUPABASE_* / DATA_SUPABASE_* are not set, both clients fall back
to the legacy SUPABASE_URL / SUPABASE_KEY (single-project mode).
"""

from __future__ import annotations

from supabase import Client, create_client

from app.config import get_settings

_auth_client: Client | None = None
_data_client: Client | None = None


def get_auth_db() -> Client:
    """Client for auth operations (JWT validation, memberships)."""
    global _auth_client
    if _auth_client is None:
        settings = get_settings()
        _auth_client = create_client(settings.auth_url, settings.auth_key)
    return _auth_client


def get_data_db() -> Client:
    """Client for data operations (budgets, items, catalogs, versions, etc.)."""
    global _data_client
    if _data_client is None:
        settings = get_settings()
        _data_client = create_client(settings.data_url, settings.data_key)
    return _data_client
