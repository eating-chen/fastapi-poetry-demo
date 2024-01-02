"""chatbot related api"""
import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.db.events import get_db
from app.models.schemas.chatbot_schema import (
    CreateChatbotInput,
    CreateChatbotOutput,
    GetAllChatbots,
    UpdateChatbotInput,
)
from app.services.chatbot_manager import CHATBOT_MANAGER

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get(
    "/chatbots",
    response_model=GetAllChatbots,
    status_code=status.HTTP_200_OK,
    tags=["Chatbot"],
    summary="取得所有chatbot",
)
def get_chatbot(_db: get_db = Depends()):
    chatbots = CHATBOT_MANAGER.get_all_chatbot(_db)
    return {"all_chatbots": chatbots}


@router.get(
    "/chatbots/{chatbot_pk}",
    response_model=CreateChatbotOutput,
    status_code=status.HTTP_200_OK,
    tags=["Chatbot"],
    summary="顯示單一chatbot",
)
def get_one_chatbot(chatbot_pk: int, _db: get_db = Depends()):
    chatbots = CHATBOT_MANAGER.get_chatbot_by_key(_db, chatbot_pk)
    return chatbots


@router.post(
    "/chatbots",
    response_model=CreateChatbotOutput,
    status_code=status.HTTP_201_CREATED,
    tags=["Chatbot"],
    summary="創建chatbot",
)
def create_chatbot(chatbot_data: CreateChatbotInput, _db: get_db = Depends()):
    db_chatbot_data = CHATBOT_MANAGER.create_service(_db, chatbot_data)

    return db_chatbot_data


@router.put(
    "/chatbots/{chatbots_id}",
    response_model=CreateChatbotOutput,
    status_code=status.HTTP_200_OK,
    tags=["Chatbot"],
    summary="更新chatbot資料",
)
def update_chatbot(chatbots_id: int, chatbot_data: UpdateChatbotInput, _db: get_db = Depends()):
    res_data = CHATBOT_MANAGER.update_chatbot_data(_db, chatbot_data, chatbots_id)
    if res_data is None:
        raise HTTPException(status_code=500, detail=f"no chatbot_id {chatbots_id}")
    return res_data


@router.delete(
    "/chatbots/{chatbots_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Chatbot"],
    summary="刪除chatbot",
)
def delete_chatbot(chatbots_id: int, _db: get_db = Depends()):
    CHATBOT_MANAGER.delete_service(_db, chatbots_id)
