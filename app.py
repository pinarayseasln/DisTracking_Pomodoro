
import importlib

from database.db import init_db

try:
    Flask = importlib.import_module("flask").Flask
except ModuleNotFoundError as exc:
    raise RuntimeError(
        "Flask is not installed. Install it with: pip install flask"
    ) from exc

from routes.home import home_bp
from routes.pomodoro import pomodoro_bp
from routes.user import user_bp
from routes.buildings import buildings_bp
from routes.tasks import tasks_bp
from routes.challenge import challenge_bp


app = Flask(__name__)

app.register_blueprint(home_bp)
app.register_blueprint(pomodoro_bp)
app.register_blueprint(user_bp)
app.register_blueprint(buildings_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(challenge_bp)

# Initialize the schema for Flask CLI and WSGI launches as well as direct runs.
init_db()


if __name__ == '__main__':
    app.run(debug=True)
