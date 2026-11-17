
from flask import Blueprint, jsonify
from models.challenge_model import get_random_question

challenge_bp = Blueprint("challenge", __name__)


@challenge_bp.route('/api/challenge/random')
def rastgele_soru():
    return jsonify(get_random_question())
