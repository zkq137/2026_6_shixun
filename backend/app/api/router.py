from fastapi import APIRouter

from app.api.v1 import admin, ai, auth, cart, catalog, health, orders, users
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])

versioned_router = APIRouter(prefix=settings.api_prefix)
versioned_router.include_router(health.router, tags=["health"])
versioned_router.include_router(auth.router, tags=["auth"])
versioned_router.include_router(users.router, tags=["users"])
versioned_router.include_router(catalog.router, tags=["catalog"])
versioned_router.include_router(cart.router, tags=["cart"])
versioned_router.include_router(orders.router, tags=["orders"])
versioned_router.include_router(admin.router, tags=["admin"])
versioned_router.include_router(ai.router, tags=["ai"])
api_router.include_router(versioned_router)
