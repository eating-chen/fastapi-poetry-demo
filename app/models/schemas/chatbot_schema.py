"""define model"""
from typing import Optional
from pydantic import BaseModel, Field

class CreateChatbotInput(BaseModel):
    chatbot_id: Optional[int] = Field(default=0, description="chatbot id，預設為0")
    description: Optional[str] = Field(default="", description="chatbot 的相關說明")

    class Config:
        from_attributes = True
        json_schema_extra = {"example": {"chatbot_id": True, "description": "chatbot test"}}

class CreateChatbotOutput(BaseModel):
    message: str = Field(..., description="chatbot 的相關說明")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": [
                {
                    "message": "chatbot test"
                }
            ]
        }

class GetAllChatbots(BaseModel):
    message: str = Field(..., description="chatbot 的相關說明")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": [
                {
                    "message": "chatbot test"
                }
            ]
        }
