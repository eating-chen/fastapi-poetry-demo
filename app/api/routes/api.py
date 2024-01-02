from fastapi import APIRouter

from app.api.routes import chatbot_router, modelmanager_router, retrieval_skill_router, slu_router

router = APIRouter()
router.include_router(chatbot_router.router)
router.include_router(retrieval_skill_router.router)
router.include_router(modelmanager_router.router, prefix="/chatbots")
router.include_router(slu_router.router, prefix="/chatbots")
