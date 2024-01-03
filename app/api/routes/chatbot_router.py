"""chatbot related api"""
from fastapi import APIRouter, status
from app.models.schemas.chatbot_schema import (
    CreateChatbotInput,
    CreateChatbotOutput,
    GetAllChatbots
)

router = APIRouter()

@router.get(
    "/chatbots",
    response_model=GetAllChatbots,
    status_code=status.HTTP_200_OK,
    tags=["Chatbot"],
    summary="取得所有chatbot",
)
def get_chatbot():
    return {"message": 'get all chatbot'}


@router.get(
    "/chatbots/{chatbot_pk}",
    response_model=CreateChatbotOutput,
    status_code=status.HTTP_200_OK,
    tags=["Chatbot"],
    summary="顯示單一chatbot",
)
def get_one_chatbot(chatbot_pk: int):
    return {"message": f'get no.{chatbot_pk} chatbot'}


@router.post(
    "/chatbots",
    response_model=CreateChatbotOutput,
    status_code=status.HTTP_201_CREATED,
    tags=["Chatbot"],
    summary="創建chatbot",
)
def create_chatbot(chatbot_data: CreateChatbotInput):
    return {"message": 'create chatbot'}
