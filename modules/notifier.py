from typing import List, Tuple
from modules.agent import Agent
import os


# Array of notes stored in a notifier
class Notes:
    def __init__(self, maxlen: int = int(os.getenv("MAXNOTES"))) -> None:
        self.maxlen = maxlen
        self.storage = dict()
        self.ids = list()

    def __getitem__(self, key: int) -> object:
        return self.storage[key]

    def get(self, key: int, default: object = None) -> object:
        return self.storage.get(key, default)

    def __setitem__(self, key: int, value: object) -> None:
        if self.storage.get(key) is None:
            self.ids.append(key)
        self.storage[key] = value
        if len(self.storage) > self.maxlen:
            k = self.ids.pop(0)
            self.storage.pop(k)

    def pop(self, key: int) -> object:
        if key == self.ids[0]:
            self.ids.pop(0)
        return self.storage.pop(key)


class Notifier:
    def __init__(self, agent: Agent, chat_id: str) -> None:
        self.agent = agent
        self.chat_id = chat_id
        self.notes = Notes()

    def send_note(self, obj: object) -> Tuple[object, int]:
        try:
            message = obj["message"]
        except KeyError:
            return "Bad Request: missing field 'message'", 400
        options = obj.get("options")
        if not options:
            reply_markup = None
            self.agent.send_message(self.chat_id, message)
            return {"ok": "OK"}, 200
        else:
            reply_markup = {"inline_keyboard": options}
            res = self.agent.send_message(
                self.chat_id, message, reply_markup=reply_markup)
            obj["status"] = "pending"
            msgid = res.json()["result"]["message_id"]
            self.notes[msgid] = obj
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
        if self.notes.get(msgid) is None:
            print(f"Warning: message {msgid} not found")
        else:
            self.notes[msgid]["status"] = "confirmed"
            self.notes[msgid]["select"] = select
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
                self.notes.pop(id)
            except KeyError:
                exs.append(id)
        return {"not_found": exs}, 200

    def get_notes(self) -> Tuple[object, int]:
        return self.notes.storage, 200
