from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    dashboard,
    defects,
    traceability,
    orders,
    lots,
    containment,
    capas,
    validation,
)

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(dashboard.router)
api_router.include_router(defects.router)
api_router.include_router(traceability.router)
api_router.include_router(orders.router)
api_router.include_router(lots.router)
api_router.include_router(containment.router)
api_router.include_router(capas.router)
api_router.include_router(validation.router)

