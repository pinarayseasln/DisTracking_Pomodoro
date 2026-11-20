from flask import Blueprint, jsonify, request

from models.pomodoro_model import (
    cancel_session as cancel_session_model,
    complete_pomodoro as complete_pomodoro_model,
    get_current_session as get_current_session_model,
    heartbeat_session as heartbeat_session_model,
    pause_session as pause_session_model,
    resume_session as resume_session_model,
    start_session as start_session_model,
)

pomodoro_bp = Blueprint("pomodoro", __name__)


def _payload():
    return request.get_json(silent=True) or request.form or {}


def _response(result):
    body, status = result
    return jsonify(body), status


@pomodoro_bp.route("/api/pomodoro/session", methods=["GET"])
def get_current_session():
    return _response(get_current_session_model())


@pomodoro_bp.route("/api/pomodoro/start", methods=["POST"])
def start_session():
    payload = _payload()
    return _response(start_session_model(
        payload.get("mode"), payload.get("duration_seconds"), payload.get("quest_id")
    ))


@pomodoro_bp.route("/api/pomodoro/heartbeat", methods=["POST"])
def heartbeat_session():
    return _response(heartbeat_session_model(_payload().get("session_id")))


@pomodoro_bp.route("/api/pomodoro/pause", methods=["POST"])
def pause_session():
    return _response(pause_session_model(_payload().get("session_id")))


@pomodoro_bp.route("/api/pomodoro/resume", methods=["POST"])
def resume_session():
    return _response(resume_session_model(_payload().get("session_id")))


@pomodoro_bp.route("/api/pomodoro/reset", methods=["POST"])
def reset_session():
    return _response(cancel_session_model(_payload().get("session_id")))


@pomodoro_bp.route("/api/pomodoro/complete", methods=["POST"])
def complete_pomodoro():
    return _response(complete_pomodoro_model(_payload().get("session_id")))
