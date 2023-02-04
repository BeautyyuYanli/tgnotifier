from modules.chats import Chats
from modules.agent import Agent


def for_api(origin_token: str, chats: Chats) -> "str | None":
    try:
        [chat_id, chat_token] = origin_token.split(':')
        chat_id = int(chat_id)
    except Exception as e:
        return None
    else:
        if chats.get_token(chat_id) == chat_token:
            return chat_id
        else:
            return None


def for_admin(get_token: str, self_token: str) -> bool:
    return get_token == self_token


def for_callback(get_token: str, agent: Agent):
    return get_token == agent.token
