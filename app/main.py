"""initial fastapi app"""
from fastapi import FastAPI
from app.api.routes.api import router as api_router

tags_metadata = [{"name": "Chatbot", "description": "chatbot相關功能"}]


def create_app() -> FastAPI:
    """create fastapi app"""
    fastapi_app = FastAPI(title="Chatbot API", debug=True, openapi_tags=tags_metadata)
    return fastapi_app


app = create_app()
app.include_router(api_router)
