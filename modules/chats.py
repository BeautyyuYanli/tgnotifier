from typing import List, Tuple
from redis import Redis
import modules.agent as agent
import modules.notifier as notifier
import os
import uuid


# State of all the chats and their corresponding notifiers
class Chats():
    def __init__(self, agent: agent.Agent, redis: Redis) -> None:
        self.agent = agent
        self.redis = redis
        self.storage = dict()
        self.token = f"chats.tokens"

    def load(self) -> None:
        t = [x.split(":") for x in os.getenv("CHAT_TOKEN").split(";")]
        self.redis.hset(self.token, mapping={x[0]: x[1] for x in t})

    def exist_chat(self, chat_id: int) -> bool:
        return self.redis.hexists(self.token, chat_id)

    def get_notifier(self, chat_id: int) -> notifier.Notifier:
        t = self.storage.get(chat_id)
        if t is None:
            t = notifier.Notifier(
                self.agent, self.redis, chat_id)
            self.storage[chat_id] = t
        return t

    def get_token(self, chat_id: int) -> "str | None":
        t = self.redis.hget(self.token, chat_id)
        if t:
            return t.decode("ascii")
        return None

    def create_token(self, chat_id: int) -> str:
        token = str(uuid.uuid4())
        self.redis.hset(self.token, chat_id, token)
        return token
