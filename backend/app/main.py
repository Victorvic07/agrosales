from fastapi import FastAPI
from app.api.routers.categories import router as categories_router
from app.api.routers.auth import router as auth_router
from app.api.routers.health import router as health_router
from app.core.config import get_settings
from app.api.routers.users import router as users_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    debug=settings.app_debug,
    version="0.1.0",
)

app.include_router(health_router, prefix=settings.api_v1_prefix)
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(users_router, prefix=settings.api_v1_prefix)
app.include_router(
    categories_router,
    prefix=settings.api_v1_prefix,
)