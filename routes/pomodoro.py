from flask import Blueprint, jsonify, request

from models.pomodoro_model import complete_pomodoro as complete_pomodoro_model

pomodoro_bp = Blueprint("pomodoro", __name__)

@pomodoro_bp.route('/api/pomodoro/complete', methods=['POST'])
def complete_pomodoro():
    payload = request.get_json(silent=True) or {}

    quest_id = payload.get("quest_id")
    focus_minutes = payload.get("focus_minutes")

    result, status_code = complete_pomodoro_model(
        quest_id,
        focus_minutes
    )

    return jsonify(result), status_code