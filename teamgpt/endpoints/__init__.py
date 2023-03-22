from fastapi import APIRouter
from teamgpt.endpoints.user import router as user_router
from teamgpt.endpoints.organization import router as organization_router
router = APIRouter()

router.include_router(user_router)
router.include_router(organization_router)
