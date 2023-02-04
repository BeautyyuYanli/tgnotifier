from typing import List, Tuple
import modules.agent as agent
import modules.notifier as notifier
import os


# State of all the chats and their corresponding notifiers
class Chats():
    def __init__(self, agent: agent.Agent) -> None:
        self.agent = agent
        self.storage = dict()
        self.tokens = dict()
        self.load()

    def load(self) -> None:
        for i in os.getenv("CHAT_TOKEN").split(";"):
            [chat_id, chat_token] = i.split(':')
            chat_id = int(chat_id)
            self.storage[chat_id] = notifier.Notifier(self.agent, chat_id)
            self.tokens[chat_id] = chat_token

    # def create_notifier(self, chat_id: str) -> notifier.Notifier:
    #     t = notifier.Notifier(self.agent, chat_id)
    #     self.storage[chat_id] = t
    #     return t

    def set_notifier_token(self, chat_id: int, token: str):
        self.tokens[chat_id] = token

    def get_notifier(self, chat_id: int) -> "notifier.Notifier | None":
        return self.storage.get(chat_id)

    def get_token(self, chat_id: int) -> "str | None":
        return self.tokens.get(chat_id)
