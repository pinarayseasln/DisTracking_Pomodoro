from flask import Blueprint, jsonify
from models.user import get_user_data

user_bp = Blueprint("user", __name__)


@user_bp.route('/api/user')
def user_info():
    user = get_user_data()

    return jsonify({
        "points": user["points"],
        "completed_sessions": user["completed_sessions"]
    })