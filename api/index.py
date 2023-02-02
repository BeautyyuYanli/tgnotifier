import json
import os
import uuid
from flask import Flask, request
import modules.agent as agent
import modules.notifier as notifier

app = Flask(__name__)
self_token = str(uuid.uuid4())
agent = agent.Agent(self_token=self_token)
notifier = notifier.Notifier(agent, os.getenv("CHAT_ID"))


@app.route('/')
def home():
    return 'Hello, World!'


@app.route('/webhook', methods=['POST'])
def webhook():
    if not request.headers.get("X-Telegram-Bot-Api-Secret-Token") == self_token:
        return "Unauthorized", 401
    if not request.headers.get("Content-Type") == "application/json":
        return "Unsupported Media Type", 415
    if request.method == 'POST':
        if request.json.get("callback_query"):
            return notifier.confirm_note(request.json)


@app.route('/send_note', methods=['POST'])
def send_note():
    if not request.headers.get("X-TGNotifier-Token") == os.getenv("BOT_TOKEN"):
        return "Unauthorized", 401
    if not request.headers.get("Content-Type") == "application/json":
        return "Unsupported Media Type", 415
    if request.method == 'POST':
        return notifier.send_note(request.json)


@app.route('/get_notes', methods=['GET'])
def get_notes():
    if not request.headers.get("X-TGNotifier-Token") == os.getenv("BOT_TOKEN"):
        return "Unauthorized", 401
    if request.method == 'GET':
        return notifier.get_notes()


@app.route('/consume_notes', methods=['POST'])
def consume_notes():
    if not request.headers.get("X-TGNotifier-Token") == os.getenv("BOT_TOKEN"):
        return "Unauthorized", 401
    if not request.headers.get("Content-Type") == "application/json":
        return "Unsupported Media Type", 415
    if request.method == 'POST':
        return notifier.consume_notes(request.json)
