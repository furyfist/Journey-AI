from supabase import acreate_client, AsyncClient

from app.core.config import settings


async def create_db_client() -> AsyncClient:
    return await acreate_client(
        settings.supabase_url,
        settings.supabase_service_key,
    )
