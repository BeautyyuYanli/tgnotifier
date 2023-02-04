import os
import modules.auth as auth
from flask import Flask, request
from modules.agent import Agent
from modules.chats import Chats

app = Flask(__name__)
agent = Agent(os.getenv("BOT_TOKEN"), os.getenv("CALLBACK_URL"))
chats = Chats(agent)


@app.route('/')
def home():
    return 'Hello, World!'


@app.route('/refresh_webhook', methods=['GET'])
def refresh_webhook():
    if not auth.for_admin(request.headers.get("X-TGNotifier-Token"), os.getenv("BOT_TOKEN")):
        return "Unauthorized", 401
    agent.set_webhook(["callback_query"])
    return "OK", 200


@app.route('/webhook', methods=['POST'])
def webhook():
    if not auth.for_callback(request.headers.get("X-Telegram-Bot-Api-Secret-Token"), agent):
        return "Unauthorized", 401
    if not request.headers.get("Content-Type") == "application/json":
        return "Unsupported Media Type", 415
    if request.method == 'POST':
        obj = request.json
        msg = obj.get("message")
        if msg:
            chat_id = msg["chat"]["id"]
            text = msg.get("text")
            print(text)
            agent.send_message(chat_id, text)

        query = obj.get("callback_query")
        if query:
            chat_id = query["message"]["chat"]["id"]
            notifier = chats.get_notifier(chat_id)
            if notifier == None:
                agent.send_message(
                    chat_id, "Unregistered chat, please use /new_token <token> to register")
                return "OK", 200
            notifier.confirm_note(obj)
    return "OK", 200


@app.route('/send_note', methods=['POST'])
def send_note():
    if not request.headers.get("Content-Type") == "application/json":
        return "Unsupported Media Type", 415
    chat_id = auth.for_api(request.headers.get(
        "X-TGNotifier-ChatToken"), chats)
    if chat_id == None:
        return "Unauthorized", 401
    notifier = chats.get_notifier(chat_id)
    if request.method == 'POST':
        return notifier.send_note(request.json)


@app.route('/get_notes', methods=['GET'])
def get_notes():
    chat_id = auth.for_api(request.headers.get(
        "X-TGNotifier-ChatToken"), chats)
    if chat_id == None:
        return "Unauthorized", 401
    notifier = chats.get_notifier(chat_id)
    if request.method == 'GET':
        return notifier.get_notes()


@app.route('/consume_notes', methods=['POST'])
def consume_notes():
    if not request.headers.get("Content-Type") == "application/json":
        return "Unsupported Media Type", 415
    chat_id = auth.for_api(request.headers.get(
        "X-TGNotifier-ChatToken"), chats)
    if chat_id == None:
        return "Unauthorized", 401
    notifier = chats.get_notifier(chat_id)
    if not request.headers.get("Content-Type") == "application/json":
        return "Unsupported Media Type", 415
    if request.method == 'POST':
        return notifier.consume_notes(request.json)
