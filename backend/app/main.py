from fastapi import FastAPI
from app.api.routers.categories import router as categories_router
from app.api.routers.auth import router as auth_router
from app.api.routers.health import router as health_router
from app.core.config import get_settings
from app.api.routers.users import router as users_router
from app.api.routers.products import router as products_router
from app.api.routers.lots import router as lots_router
from app.api.routers.product_variations import (
    router as product_variations_router,
)
from app.api.routers.inventory_movements import (
    router as inventory_movements_router,
)
from app.api.routers.stock_reservations import (
    router as stock_reservations_router,
)
from app.api.routers.customers import router as customers_router


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
app.include_router(
    products_router,
    prefix=settings.api_v1_prefix,
)
app.include_router(
    product_variations_router,
    prefix=settings.api_v1_prefix,
)
app.include_router(
    lots_router,
    prefix=settings.api_v1_prefix,
)
app.include_router(
    inventory_movements_router,
    prefix=settings.api_v1_prefix,
)
app.include_router(
    stock_reservations_router,
    prefix=settings.api_v1_prefix,
)
app.include_router(
    customers_router,
    prefix=settings.api_v1_prefix,
)