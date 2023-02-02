from flask import Flask, request
from modules import hello
import json
import os

import modules.agent as agent
import modules.notifier as notifier

app = Flask(__name__)
agent = agent.Agent()
notifier = notifier.Notifier(agent)


@app.route('/')
def home():
    return 'Hello, World!'


@app.route('/webhook', methods=['POST'])
def webhook():
    if not request.headers.get("X-Telegram-Bot-Api-Secret-Token") == os.getenv("SELF_TOKEN"):
        return "Unauthorized", 401
    if not request.headers.get("Content-Type") == "application/json":
        return "Unsupported Media Type", 415
    if request.method == 'POST':
        if request.json.get("callback_query"):
            return notifier.confirm_note(request.json)

        if request.json.get("channel_post"):
            return notifier.produce_note(
                {
                    "message": f"forward post: t.me/{request.json['channel_post']['chat']['username']}/{request.json['channel_post']['message_id']} ?",
                    "options": [[{"text": "Yes", "callback_data": "yes"}, {"text": "No", "callback_data": "no"}]]
                }
            )


@app.route('/send_note', methods=['POST'])
def send_note():
    if not request.headers.get("X-TGNotifier-Token") == os.getenv("SELF_TOKEN"):
        return "Unauthorized", 401
    if not request.headers.get("Content-Type") == "application/json":
        return "Unsupported Media Type", 415
    if request.method == 'POST':
        return notifier.send_note(request.json)


@app.route('/get_notes', methods=['GET'])
def get_notes():
    if not request.headers.get("X-TGNotifier-Token") == os.getenv("SELF_TOKEN"):
        return "Unauthorized", 401
    if request.method == 'GET':
        return notifier.get_notes()


@app.route('/consume_notes', methods=['POST'])
def consume_notes():
    if not request.headers.get("X-TGNotifier-Token") == os.getenv("SELF_TOKEN"):
        return "Unauthorized", 401
    if not request.headers.get("Content-Type") == "application/json":
        return "Unsupported Media Type", 415
    if request.method == 'POST':
        return notifier.consume_notes(request.json)
