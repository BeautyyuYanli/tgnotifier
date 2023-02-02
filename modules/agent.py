import os
import json
import requests


class Agent:
    def __init__(self, self_token: str) -> None:
        self.bot_token = os.getenv("BOT_TOKEN")
        self.session = requests.Session()
        self.callback_url = os.getenv("CALLBACK_URL")
        self.set_webhook(self_token=self_token)

    def set_webhook(
        self,
        self_token: str,
        allow_updates: list[str] = ["callback_query"]
    ) -> requests.Response:
        url = f"https://api.telegram.org/bot{self.bot_token}/setWebhook"
        data = {
            "url": self.callback_url,
            "allowed_updates": json.dumps(allow_updates),
            "secret_token": self_token
        }
        return self.session.post(url, data=data)

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
