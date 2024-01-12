# so_outward_api

from fastapi import APIRouter
from src.routes.user import router as test_rotuer
from src.routes.address import router as addr_router
router = APIRouter()

# db environment
router.include_router(test_rotuer)
router.include_router(addr_router)