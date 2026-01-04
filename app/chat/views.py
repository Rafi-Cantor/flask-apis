from app import socketio
from flask_socketio import emit, join_room, leave_room
from objects import user, user_chat_mapping, chat, message
from utils.socket_auth import authenticate_socket, socket_auth_required
from flask import session


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
        socketio.emit("error", {
            "error_message": "User is not in chat"
        })
    leave_room(chat_id)
    socketio.emit("success", {"message": "You have left the chat!"})


@socketio.on("send_message", namespace="/chat-app")
@socket_auth_required
def send_message(data):
    chat_id = data["chat_id"]
    content = data["content"]
    user_id = session.get("user_id")
    try:
        user_chat_mapping.UserChatMapping.get_chats_for_user(user_id)
    except user_chat_mapping.UserChatMappingDoesntExist:
        emit("error", {"error_message": "Not authorized for this chat"})
        return

    message.Message.create(chat_id=chat_id, content=content, sent_by=user_id)
    payload = {
        "sent_by": user_id,
        "content": content
    }

    emit("new_message", payload, room=chat_id)





