
from flask import Blueprint, jsonify, request
from models.building import buy_building as buy_building_model
from models.building import get_market_items

buildings_bp = Blueprint("buildings", __name__)


@buildings_bp.route("/api/market/buildings", methods=["GET"])
def market_buildings():
    return jsonify({
        "success": True,
        "items": get_market_items()
    })


@buildings_bp.route("/api/building/buy", methods=["POST"])
def buy_building():
    payload = request.get_json(silent=True) or {}
    building_type = payload.get("building_type", "shelter")

    result, status_code = buy_building_model(building_type)

    return jsonify(result), status_code
