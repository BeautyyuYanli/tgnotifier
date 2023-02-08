from typing import List, Tuple
from modules.agent import Agent
import os
from redis import Redis
from redis.commands.json.path import Path
import json


# Array of notes stored in a notifier
class Notes:
    def __init__(self, chat_id: int, redis: Redis, maxlen: int = int(os.getenv("MAXNOTES"))) -> None:
        self.redis = redis
        self.key = f"chats:{chat_id}:notes"
        self.maxlen = maxlen

    def get_note(self, key: int) -> "object | None":
        try:
            return json.loads(self.redis.zrange(self.key, key, key, byscore=True)[0])
        except Exception:
            return None

    def get_all_notes(self) -> object:
        t = self.redis.zrange(self.key, 0, -1, withscores=True)
        t = {int(i[1]): json.loads(i[0]) for i in t}
        return t

    def set_note(self, key: int, value: object) -> None:
        self.del_note(key)
        self.redis.zadd(self.key, {json.dumps(value): key})
        self.redis.zremrangebyrank(self.key, 0, -self.maxlen - 1)

    def del_note(self, key: int) -> None:
        self.redis.zremrangebyscore(self.key, key, key)


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
        additional_data = obj.get("additional_data")
        if not options:
            self.agent.send_message(self.chat_id, message)
            return {"ok": "OK"}, 200
        else:
            reply_markup = {"inline_keyboard": options}
            res = self.agent.send_message(
                self.chat_id, message, reply_markup=reply_markup, additional_data=additional_data)
            obj["status"] = "pending"
            msgid = res.json()["result"]["message_id"]
            obj["id"] = msgid
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
        note = self.notes.get_note(msgid)
        if note is None:
            print(f"Warning: message {msgid} not found")
        else:
            note["status"] = "confirmed"
            note["select"] = select
            self.notes.set_note(msgid, note)
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
