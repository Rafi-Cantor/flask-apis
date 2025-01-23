from flask import Flask, request, jsonify
from flask_cors import CORS


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

    from app.movie_app import movie_app as movie_blueprint
    app.register_blueprint(movie_blueprint, url_prefix="/movie_app")

    from app.car_data_app import car_data_app as car_data_blueprint
    app.register_blueprint(car_data_blueprint, url_prefix="/car_data_app")

    return app
