
from flask import Blueprint, render_template
from models.user import get_user_data, get_user_buildings

home_bp = Blueprint("home", __name__)


@home_bp.route('/')
def ana_sayfa():
    user = get_user_data()
    buildings = get_user_buildings()

    return render_template(
        "index.html",
        points=user["points"],
        completed_sessions=user["completed_sessions"],
        buildings=buildings
    )
