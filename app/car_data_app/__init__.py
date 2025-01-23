from flask import Blueprint

car_data_app = Blueprint('car_data_app', __name__)

from app.car_data_app import views
