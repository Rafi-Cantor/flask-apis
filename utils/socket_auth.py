from flask import session
from flask_socketio import emit, disconnect
from app.auth.views import verify_token
from functools import wraps

def authenticate_socket(token: str):
    user_obj = verify_token(token)
    if not user_obj:
        return None
    session["user_id"] = user_obj.user_id
    return user_obj


def socket_auth_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            emit("error", {"error": "Unauthorized"})
            disconnect()
            return
        return fn(*args, **kwargs)
    return wrapper
