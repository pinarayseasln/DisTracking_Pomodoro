from flask import Blueprint, jsonify, request

from models.city import (
    complete_city_stage as complete_city_stage_model,
    get_city_state,
    place_city_decoration as place_city_decoration_model,
)


city_bp = Blueprint("city", __name__)


@city_bp.route("/api/cities/<city_id>/rebuild", methods=["GET"])
def city_rebuild_state(city_id):
    state = get_city_state(city_id)
    if state is None:
        return jsonify({"success": False, "message": "This city is not available yet."}), 404
    return jsonify({"success": True, **state})


@city_bp.route("/api/cities/<city_id>/rebuild/complete", methods=["POST"])
def complete_city_stage(city_id):
    result, status = complete_city_stage_model(city_id)
    return jsonify(result), status


@city_bp.route("/api/cities/<city_id>/decorations/place", methods=["POST"])
def place_city_decoration(city_id):
    payload = request.get_json(silent=True) or {}
    result, status = place_city_decoration_model(
        city_id,
        payload.get("slot_id"),
        payload.get("decoration_id"),
    )
    return jsonify(result), status
