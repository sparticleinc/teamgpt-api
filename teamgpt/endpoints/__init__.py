from fastapi import APIRouter
from teamgpt.endpoints.user import router as user_router
from teamgpt.endpoints.organization import router as organization_router
from teamgpt.endpoints.gptkey import router as gpt_key_router
from teamgpt.endpoints.conversations import router as conversations_router
from teamgpt.endpoints.aicharacter import router as ai_character_router
from teamgpt.endpoints.sysgptkey import router as sys_gpt_key_router
from teamgpt.endpoints.gptprompt import router as gpt_prompt_router

router = APIRouter(prefix="/api/v1")

router.include_router(user_router)
router.include_router(organization_router)
router.include_router(gpt_key_router)
router.include_router(conversations_router)
router.include_router(ai_character_router)
router.include_router(sys_gpt_key_router)
router.include_router(gpt_prompt_router)
