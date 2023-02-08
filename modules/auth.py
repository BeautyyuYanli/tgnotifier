from typing import Tuple
from modules.chats import Chats
from modules.agent import Agent
from flask import Request


class Auth:
    """header checker
    """
    def for_api(request: Request, chats: Chats) -> "int | Tuple[str, int]":
        """authentications for api call

        return chat_id if token is valid, else return Flask response
        """
        if not request.headers.get("Content-Type") == "application/json":
            return "Unsupported Media Type", 415
        origin_token = request.headers.get("X-TGNotifier-ChatToken")
        try:
            [chat_id, chat_token] = origin_token.split(':')
            chat_id = int(chat_id)
        except Exception as e:
            return None
        else:
            if chats.get_token(chat_id) == chat_token:
                return chat_id
            else:
                return "Unauthorized", 401

    def for_admin(request: Request, token: str) -> "None | Tuple[str, int]":
        """authentications for admin call

        return None if token is valid, else return Flask response
        """
        if request.headers.get("X-TGNotifier-BotToken") == token:
            return None
        else:
            return "Unauthorized", 401

    def for_webhook(request: Request, agent: Agent) -> "None | Tuple[str, int]":
        """authentications for webhook

        return None if token is valid, else return Flask response
        """
        if not request.headers.get("Content-Type") == "application/json":
            return "Unsupported Media Type", 415
        if request.headers.get("X-Telegram-Bot-Api-Secret-Token") == agent.token:
            return None
        else:
            return "Unauthorized", 401
