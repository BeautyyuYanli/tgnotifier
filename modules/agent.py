import os
import json
import requests


# Agent of telegram bot api
class Agent:
    def __init__(self, token: str, callback_url: str) -> None:
        self.bot_token = token
        [self.id, self.token] = token.split(":")
        self.id = int(self.id)
        self.session = requests.Session()
        self.callback_url = callback_url

    def set_commands(self, commands: "None | list[dict]" = None):
        self.session.get(
            f"https://api.telegram.org/bot{self.bot_token}/deleteMyCommands")
        if commands:
            res = self.session.post(
                url=f"https://api.telegram.org/bot{self.bot_token}/setMyCommands",
                json={
                    "commands": commands
                }
            )
            return res

    def set_webhook(
        self,
        allow_updates: list[str]
    ) -> requests.Response:
        self.session.get(
            f"https://api.telegram.org/bot{self.bot_token}/deleteWebhook")
        url = f"https://api.telegram.org/bot{self.bot_token}/setWebhook"
        json = {
            "url": self.callback_url,
            "allowed_updates": allow_updates,
            "secret_token": self.token
        }
        res = self.session.post(url, json=json)
        return res

    def answer_callback_query(
            self,
            callback_query_id: str,
            text: "str | None" = None,
            show_alert: bool = False
    ) -> requests.Response:
        apiurl = f"https://api.telegram.org/bot{self.bot_token}/answerCallbackQuery"
        data = {
            "callback_query_id": callback_query_id,
            "show_alert": show_alert,
        }
        if text:
            data["text"] = text
        return self.session.post(apiurl, data=data)

    def send_message(
        self,
        chat_id: str,
        message: str,
        parse_mode: "None | str" = None,
        reply_markup: "None | object" = None,
        additional_data: "None | object" = None
    ) -> requests.Response:
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": message
        }
        if parse_mode:
            data["parse_mode"] = parse_mode
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        if additional_data:
            data.update(additional_data)
        res = self.session.post(url, data=data)
        return res

    def edit_message_replymarkup(
        self,
        chat_id: str,
        message_id: int,
        reply_markup: "None | object" = None,
    ) -> requests.Response:
        url = f"https://api.telegram.org/bot{self.bot_token}/editMessageReplyMarkup"
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "reply_markup": ""
        }
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        res = self.session.post(url, data=data)
        return res
