from fastapi import APIRouter
from app.api.routes import chatbot_router

router = APIRouter()
router.include_router(chatbot_router.router)
