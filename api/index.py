import os
import modules.auth as auth
from flask import Flask, request
from modules.agent import Agent
from modules.chats import Chats
from redis import Redis

app = Flask(__name__)
redis = Redis(
    os.getenv("REDIS_HOST"),
    int(os.getenv("REDIS_PORT")),
    int(os.getenv("REDIS_DB")),
    os.getenv("REDIS_PASSWORD")
)
agent = Agent(os.getenv("BOT_TOKEN"), os.getenv("CALLBACK_URL"))
chats = Chats(agent, redis)
update_id = -1


@ app.route('/')
def home():
    return 'Hello, World!'


@ app.route('/refresh', methods=['GET'])
def refresh():
    if not auth.for_admin(request.headers.get("X-TGNotifier-BotToken"), os.getenv("BOT_TOKEN")):
        return "Unauthorized", 401
    t = agent.set_commands(
        [{"command": "new_token", "description": "Generate a new token for this chat"}])
    print(t.content, t.status_code)
    agent.set_webhook(["callback_query", "message"])
    return "OK", 200


@app.route('/load_chats', methods=['GET'])
def load_chats():
    if not auth.for_admin(request.headers.get("X-TGNotifier-BotToken"), os.getenv("BOT_TOKEN")):
        return "Unauthorized", 401
    chats.load()
    return "OK", 200


@ app.route('/webhook', methods=['POST'])
def webhook():
    if not auth.for_callback(request.headers.get("X-Telegram-Bot-Api-Secret-Token"), agent):
        return "Unauthorized", 401
    if not request.headers.get("Content-Type") == "application/json":
        return "Unsupported Media Type", 415
    if request.method == 'POST':
        obj = request.json
        global update_id
        if obj.get("update_id") <= update_id:
            return "OK", 200
        else:
            update_id = obj.get("update_id")
        msg = obj.get("message")
        if msg:
            chat_id = msg["chat"]["id"]
            text = msg.get("text")
            if text == "/new_token":
                t = chats.create_token(chat_id)
                agent.send_message(chat_id, f"New token created: {t}")
            else:
                agent.send_message(chat_id, "Unknown command")
            return "OK", 200

        query = obj.get("callback_query")
        if query:
            chat_id = query["message"]["chat"]["id"]
            if not chats.exist_chat(chat_id):
                agent.send_message(
                    chat_id, "Unregistered chat, please use /new_token <token> to register")
                return "OK", 200
            chats.get_notifier(chat_id).confirm_note(obj)
            return "OK", 200


@ app.route('/send_note', methods=['POST'])
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


@ app.route('/get_notes', methods=['GET'])
def get_notes():
    chat_id = auth.for_api(request.headers.get(
        "X-TGNotifier-ChatToken"), chats)
    if chat_id == None:
        return "Unauthorized", 401
    notifier = chats.get_notifier(chat_id)
    if request.method == 'GET':
        return notifier.get_notes()


@ app.route('/consume_notes', methods=['POST'])
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
