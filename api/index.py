import os
from redis import Redis
from flask import Flask, request
from modules.auth import Auth
from modules.agent import Agent
from modules.chats import Chats
from modules.update_id import UpdateID

app = Flask(__name__)
redis = Redis(
    os.getenv("REDIS_HOST"),
    int(os.getenv("REDIS_PORT")),
    int(os.getenv("REDIS_DB")),
    os.getenv("REDIS_PASSWORD")
)
agent = Agent(os.getenv("BOT_TOKEN"), os.getenv("CALLBACK_URL"))
chats = Chats(agent, redis)
update_id = UpdateID()


@ app.route('/')
def home():
    return 'Hello, World!'


@ app.route('/refresh', methods=['GET'])
def refresh():
    auth = Auth.for_admin(request, os.getenv("BOT_TOKEN"))
    if auth is not None:
        return auth
    t = agent.set_commands(
        [{"command": "new_token", "description": "Generate a new token for this chat"}])
    print(t.content, t.status_code)
    agent.set_webhook(["callback_query", "message"])
    return "OK", 200


@app.route('/load_chats', methods=['GET'])
def load_chats():
    auth = Auth.for_admin(request, os.getenv("BOT_TOKEN"))
    if auth is not None:
        return auth
    chats.load()
    return "OK", 200


@ app.route('/webhook', methods=['POST'])
def webhook():
    auth = Auth.for_webhook(request, agent)
    if auth is not None:
        return auth
    if request.method == 'POST':
        obj = request.json
        # compare update_id
        if not update_id.compare(obj.get("update_id")):
            return "OK", 200

        # case: message
        msg = obj.get("message")
        if msg:
            chat_id = msg["chat"]["id"]
            text = msg.get("text")
            # case: new_token
            if text == "/new_token":
                t = chats.create_token(chat_id)
                agent.send_message(chat_id, f"New token created: {t}")
            else:
                agent.send_message(chat_id, "Unknown command")
            return "OK", 200

        # case: callback_query
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
    chat_id = Auth.for_api(request, chats)
    if type(chat_id) != int:
        return chat_id
    notifier = chats.get_notifier(chat_id)
    if request.method == 'POST':
        return notifier.send_note(request.json)


@ app.route('/get_notes', methods=['GET'])
def get_notes():
    chat_id = Auth.for_api(request, chats)
    if type(chat_id) != int:
        return chat_id
    notifier = chats.get_notifier(chat_id)
    if request.method == 'GET':
        return notifier.get_notes()


@ app.route('/consume_notes', methods=['POST'])
def consume_notes():
    chat_id = Auth.for_api(request, chats)
    if type(chat_id) != int:
        return chat_id
    notifier = chats.get_notifier(chat_id)
    if not request.headers.get("Content-Type") == "application/json":
        return "Unsupported Media Type", 415
    if request.method == 'POST':
        return notifier.consume_notes(request.json)
