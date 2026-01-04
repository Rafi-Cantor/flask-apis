from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

socketio = SocketIO()


def create_app():
    app = Flask(__name__)
    CORS(app=app)

    @app.before_request
    def before_request():
        headers = {'Access-Control-Allow-Origin': '*',
                   'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                   'Access-Control-Allow-Headers': 'Content-Type'}
        if request.method.lower() == 'options':
            return jsonify(headers), 200

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/")
    from app.chat import chat as chat_blueprint
    app.register_blueprint(chat_blueprint, url_prefix="/chat")

    socketio.init_app(app)
    return app
