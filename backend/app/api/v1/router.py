from fastapi import APIRouter

from app.api.v1.endpoints import auth, items, dashboard, export

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router)
api_router.include_router(items.router)
api_router.include_router(dashboard.router)
api_router.include_router(export.router)
