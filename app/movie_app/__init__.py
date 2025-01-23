from flask import Blueprint

movie_app = Blueprint('movie_app', __name__)

from app.movie_app import views