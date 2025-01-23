import logging

from app.auth.views import basic_auth
from flask import request, jsonify
from app.car_data_app import car_data_app
import requests
import settings


@car_data_app.route("/get_vehicle_details", methods=["POST"])
@basic_auth.login_required
def get_vehicle_details():
    data = request.get_json()
    registration_number = data.get('registration_number')
    if not registration_number:
        return jsonify({"message": "Please supply a registration number"}), 400
    url = "https://driver-vehicle-licensing.api.gov.uk/vehicle-enquiry/v1/vehicles"
    headers = {
        "x-api-key": settings.DVLA_API_KEY,
        "Content-Type": "application/json",
    }
    data = {
        "registrationNumber": registration_number
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 404:
        return jsonify({"message": f"No vehicle found. "}), 404

    vehicle_data = response.json()
    make = vehicle_data["make"]
    year = vehicle_data["yearOfManufacture"]
    colour = vehicle_data["colour"]
    fuel_type = vehicle_data["fuelType"]

    return jsonify({"Make": make, "Year": year, "Colour": colour, "Fuel Type": fuel_type}), 200
