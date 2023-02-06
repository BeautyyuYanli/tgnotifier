from typing import List, Tuple
from modules.agent import Agent
import os
from redis import Redis
from redis.commands.json.path import Path


# Array of notes stored in a notifier
class Notes:
    def __init__(self, chat_id: int, redis: Redis, maxlen: int = int(os.getenv("MAXNOTES"))) -> None:
        self.redis = redis
        self.val = f"chats:{chat_id}:notes.val"
        self.id = f"chats:{chat_id}:notes.id"
        self.maxlen = maxlen
        if redis.exists(self.val) == 0:
            redis.json().set(self.val, Path("$"), {})

    def __getitem__(self, key: str) -> object:
        return self.redis.json().get(self.val, Path(f"$.{key}"))[0]

    def get_note(self, key: int) -> object | None:
        try:
            return self[str(key)]
        except Exception:
            return None

    def get_all_notes(self) -> object:
        return self.redis.json().get(self.val, Path("$"))[0]

    def __setitem__(self, key: str, value: object) -> None:
        self.redis.json().set(self.val, Path(f"$.{key}"), value)

    def set_note(self, key: int, value: object) -> None:
        if self.get_note(key) is None:
            len = self.redis.json().objlen(self.val, Path("$"))[0]
            if len >= self.maxlen:
                llen = self.redis.llen(self.id)
                for _ in range(llen):
                    k = int(self.redis.rpop(self.id))
                    v = self.get_note(k)
                    if v != None:
                        self.del_note(k)
                        break
        self[str(key)] = value
        self.redis.lpush(self.id, key)

    def del_note(self, key: int) -> None:
        key = str(key)
        self.redis.json().delete(self.val, Path(f"$.{key}"))


class Notifier:
    def __init__(self, agent: Agent, redis: Redis, chat_id: str) -> None:
        self.agent = agent
        self.chat_id = chat_id
        self.notes = Notes(chat_id, redis)

    def send_note(self, obj: object) -> Tuple[object, int]:
        try:
            message = obj["message"]
        except KeyError:
            return "Bad Request: missing field 'message'", 400
        options = obj.get("options")
        if not options:
            self.agent.send_message(self.chat_id, message)
            return {"ok": "OK"}, 200
        else:
            reply_markup = {"inline_keyboard": options}
            res = self.agent.send_message(
                self.chat_id, message, reply_markup=reply_markup)
            obj["status"] = "pending"
            msgid = res.json()["result"]["message_id"]
            self.notes.set_note(msgid, obj)
            return {"ok": "OK", "message_id": msgid}, 200

    def confirm_note(self, obj: object) -> Tuple[object, int]:
        try:
            select = obj["callback_query"]["data"]
            msgid = obj["callback_query"]["message"]["message_id"]
            qryid = obj["callback_query"]["id"]
        except KeyError:
            return "Bad Request: missing field. The webhook should only be called by Telegram server", 400
        self.agent.answer_callback_query(qryid)
        self.agent.edit_message_replymarkup(
            self.chat_id,
            msgid,
            {"inline_keyboard": [
                [{"text": select, "callback_data": select}]]}
        )
        if self.notes.get_note(msgid) is None:
            print(f"Warning: message {msgid} not found")
        else:
            self.notes[f"{msgid}.status"] = "confirmed"
            self.notes[f"{msgid}.select"] = select
        return "OK", 200

    def consume_notes(self, obj: object) -> Tuple[object, int]:
        try:
            ids = list(obj)
            for id in ids:
                if not isinstance(id, int):
                    raise TypeError
        except Exception as e:
            return "Bad Request: request body should be an array of int", 400
        exs = []
        for id in ids:
            try:
                self.notes.del_note(id)
            except KeyError:
                exs.append(id)
        return {"not_found": exs}, 200

    def get_notes(self) -> Tuple[object, int]:
        return self.notes.get_all_notes(), 200
