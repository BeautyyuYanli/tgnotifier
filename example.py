import os
import json
import requests
import argparse
baseurl = "https://tgnotifier.beautyyu.one/"
headers = {
    "X-TGNotifier-BotToken": "",
    "X-TGNotifier-ChatToken": "",
    "Content-Type": "application/json"
}


def send():
    url = f"{baseurl}send_note"
    data = {
        "message": "test, [link](https://www.google.com)",
        "options": [
            [{"text": "Button 1", "callback_data": "111"}],
            [
                {"text": "Button 2", "callback_data": "222"},
                {"text": "Button 3", "callback_data": "333"}
            ]
        ],
        "additional_data": {
            "parse_mode": "MarkdownV2",
            # "disable_notification": True,
            # "disable_web_page_preview": True
        }
    }
    res = requests.post(url, data=json.dumps(data), headers=headers)
    return res.content


def consume(data):
    url = f"{baseurl}consume_notes"
    res = requests.post(url, data=json.dumps(data), headers=headers)
    return res.content


def get():
    url = f"{baseurl}get_notes"
    res = requests.get(url, headers=headers)
    return res.content


def refresh():
    url = f"{baseurl}refresh"
    res = requests.get(url, headers=headers)
    return res.content


def load_chats():
    url = f"{baseurl}load_chats"
    res = requests.get(url, headers=headers)
    return res.content


parser = argparse.ArgumentParser()
parser.add_argument('cmd', type=str, choices=[
                    "send", "consume", "get", "refresh", "load"])
parser.add_argument('consume_data', type=int, nargs='*')
args = parser.parse_args()
if args.cmd == "send":
    print(send())
elif args.cmd == "consume":
    print(consume(args.consume_data))
elif args.cmd == "get":
    print(get())
elif args.cmd == "refresh":
    print(refresh())
elif args.cmd == "load":
    print(load_chats())
