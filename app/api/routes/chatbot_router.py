"""chatbot related api"""
from fastapi import APIRouter, status
from app.models.schemas.chatbot_schema import (
    CreateChatbot,
    GetAllChatbots,
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
    """
    get all chatbot
    """
    return {"message": "get all chatbot"}


@router.get(
    "/chatbots/{chatbot_pk}",
    response_model=CreateChatbot,
    status_code=status.HTTP_200_OK,
    tags=["Chatbot"],
    summary="顯示單一chatbot",
)
def get_one_chatbot(chatbot_pk: int):
    """
    get a chatbot

    - **chatbot_pk**: chatbot id
    """
    return {"chatbot_id": chatbot_pk, "description": "chatbot test"}


@router.post(
    "/chatbots",
    response_model=CreateChatbot,
    status_code=status.HTTP_201_CREATED,
    tags=["Chatbot"],
    summary="創建chatbot",
)
def create_chatbot(chatbot_data: CreateChatbot):
    """
    Create an chatbot

    - **chatbot_id**: chatbot id，預設為0
    - **description**: chatbot 的相關說明
    """
    return chatbot_data
