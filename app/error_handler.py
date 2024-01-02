import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class ChatbotException(Exception):
    """找不到 chatbot 或 未建立 skill manager"""

    def __init__(self, chatbot_id: int, chatbot_exist: bool, skill_name: str = None):
        self.chatbot_id = chatbot_id
        self.chatbot_exist = chatbot_exist
        self.skill_name = skill_name

    def get_message(self):
        if self.chatbot_exist:
            return f"chatbot {self.chatbot_id} have no {self.skill_name} skill yet!"
        else:
            return f"chatbot {self.chatbot_id} is not exist!"


def add_chatbot_exception_handler(app: FastAPI) -> None:
    @app.exception_handler(ChatbotException)
    def chatbot_exception_handler(request: Request, exc: ChatbotException):
        logging.error(exc.get_message())
        return JSONResponse(
            status_code=400,
            content={"detail": exc.get_message()},
        )
