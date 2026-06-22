from fastapi import APIRouter

from app.api.v1 import auth, catalog, health, users
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])

versioned_router = APIRouter(prefix=settings.api_prefix)
versioned_router.include_router(health.router, tags=["health"])
versioned_router.include_router(auth.router, tags=["auth"])
versioned_router.include_router(users.router, tags=["users"])
versioned_router.include_router(catalog.router, tags=["catalog"])
api_router.include_router(versioned_router)
