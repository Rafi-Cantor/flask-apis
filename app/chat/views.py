from app import socketio
from app.auth import views
from flask_socketio import emit, join_room, leave_room
from objects import user, user_chat_mapping, chat, message
from utils.socket_auth import authenticate_socket, socket_auth_required
from flask import session, request, jsonify
from app.chat import chat
import uuid

@socketio.on("connect", namespace="/chat-app")
def connect(auth):
    token = auth.get("token")
    user_obj = authenticate_socket(token)
    if not user_obj:
        return False


@socketio.on("leave_chat", namespace="/chat-app")
@socket_auth_required
def leave_chat(data):
    chat_id = data["chat_id"]
    user_id = session.get("user_id")
    try:
        user_chat_mapping.UserChatMapping.delete(user_id=user_id, chat_id=chat_id)
    except user_chat_mapping.UserChatMappingDoesntExist:
        emit("error", {
            "error_message": "User is not in chat"
        })
        return
    leave_room(chat_id)
    emit("success", {"message": "You have left the chat!"})


@socketio.on("send_message", namespace="/chat-app")
@socket_auth_required
def send_message(data):
    chat_id = data["chat_id"]
    content = data["content"]
    user_id = session.get("user_id")
    try:
        user_chat_mapping.UserChatMapping.check_exists(user_id=user_id, chat_id=chat_id)
    except user_chat_mapping.UserChatMappingDoesntExist:
        emit("error", {"error_message": "Not authorized for this chat"})
        return

    message.Message.create(chat_id=chat_id, content=content, sent_by=user_id)
    payload = {
        "sent_by": user_id,
        "content": content
    }

    emit("new_message", payload, room=chat_id)


@socketio.on("join_chat", namespace="/chat-app")
@socket_auth_required
def join_chat(data):
    chat_id = data["chat_id"]
    share_code = data["share_code"]
    user_id = session.get("user_id")
    try:
        chat.Chat.get_by_share_code(share_code)
        user_chat_mapping.UserChatMapping.create(user_id=user_id, chat_id=chat_id)
    except chat.ShareCodeDoesntExist:
        emit("error", {
            "error_message": f"Invalid share code - {share_code}"
        })
        return
    except user_chat_mapping.UserChatMappingDoesntExist:
        emit("error", {
            "error_message": "User is not in chat"
        })
        return
    join_room(chat_id)
    emit("success", {"message": "Welcome to the chat!"})


@chat.route("/create_new_chat", methods=["POST"])
@views.multi_auth.login_required
def create_new_chat():
    data = request.get_json()
    chat_title = data.get('title')
    current_user = views.multi_auth.current_user()
    c = chat.Chat.create(title=chat_title, user_id=current_user.user_id)

    return jsonify({
        'message': f"New chat created - {chat_title}",
        "data": {
            "chat_id": c.chat_id,
            "created_at": c.created_at,
            "share_code": c.share_code,
            "title": c.title,
            "created_by": c.created_by
    }
    }), 201


@chat.route("/users/<uuid:user_id>/chats", methods=["GET"])
@views.multi_auth.login_required
def get_chats(user_id: uuid.UUID):
    user_chats = user_chat_mapping.UserChatMapping.get_chats_for_user(user_id=user_id)
    return jsonify({"user_chats": user_chats}), 200


@chat.route("/chats/<uuid:chat_id>/messages", methods=["GET"])
@views.multi_auth.login_required
def get_chat(chat_id: uuid.UUID):
    chat_messages = message.Messages.get_messages_by_chat_id(chat_id=chat_id)
    return jsonify({"messages": chat_messages}), 200
