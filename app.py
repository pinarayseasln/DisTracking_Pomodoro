
from flask import Flask, jsonify, render_template, request
import random
import sqlite3

from task_library import CATEGORIES, get_catalog, get_task
from task_strategies import TaskRecommendationContext

app = Flask(__name__)

# Veritabanı bağlantısı
def get_db():
    conn = sqlite3.connect("distracking.db")
    conn.row_factory = sqlite3.Row
    return conn


# Veritabanını oluştur
def init_db():
    conn = get_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            id INTEGER PRIMARY KEY,
            points INTEGER NOT NULL DEFAULT 0,
            completed_sessions INTEGER NOT NULL DEFAULT 0
        )
    """)

    conn.execute("""
        INSERT OR IGNORE INTO user_data (id, points, completed_sessions)
        VALUES (1, 0, 0)
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS task_completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id TEXT NOT NULL,
            category TEXT NOT NULL,
            xp INTEGER NOT NULL,
            completed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# Mevcut kullanıcı bilgilerini getir
def get_user_data():
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM user_data WHERE id = 1"
    ).fetchone()
    conn.close()
    return user


# Mini görevler / quiz soruları
sorular = [
    {
        "soru": "Python hangi yıl piyasaya sürülmüştür?",
        "secenekler": ["1989", "1991", "2000", "2005"],
        "cevap": "1991"
    },
    {
        "soru": "Flask nedir?",
        "secenekler": [
            "Veritabanı",
            "Oyun Motoru",
            "Web Çerçevesi (Framework)",
            "İşletim Sistemi"
        ],
        "cevap": "Web Çerçevesi (Framework)"
    },
    {
        "soru": "Python'da yorum satırı hangi sembolle başlar?",
        "secenekler": ["//", "/*", "<!--", "#"],
        "cevap": "#"
    }
]

# Ana sayfa
@app.route('/')
def ana_sayfa():
    user = get_user_data()

    return render_template(
        "index.html",
        points=user["points"],
        completed_sessions=user["completed_sessions"]
         )


# Pomodoro tamamlanınca puan kazan
@app.route('/api/pomodoro/complete', methods=['POST'])
def complete_pomodoro():

    conn = get_db()

    conn.execute("""
        UPDATE user_data
        SET points = points + 10,
            completed_sessions = completed_sessions + 1
        WHERE id = 1
    """)

    conn.commit()

    user = conn.execute(
        "SELECT * FROM user_data WHERE id = 1"
    ).fetchone()

    conn.close()

    return jsonify({
        "success": True,
        "points": user["points"],
        "completed_sessions": user["completed_sessions"]
    })


# Puan bilgilerini getir
@app.route('/api/user')
def user_info():
    user = get_user_data()

    return jsonify({
        "points": user["points"],
        "completed_sessions": user["completed_sessions"]
    })


@app.route('/tasks')
def tasks_page():
    return render_template("tasks.html", categories=get_catalog())


@app.route('/api/tasks')
def task_catalog():
    return jsonify({"categories": get_catalog(), "task_count": sum(len(category["tasks"]) for category in get_catalog())})


@app.route('/api/tasks/recommend', methods=['POST'])
def recommend_task():
    payload = request.get_json(silent=True) or {}
    need = payload.get("need")
    context = TaskRecommendationContext.for_need(need)
    if context is None:
        return jsonify({"success": False, "error": "Choose a valid focus state."}), 400

    try:
        max_duration = max(1, min(5, int(payload.get("max_duration", 3))))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Choose a valid break duration."}), 400

    exclude_ids = payload.get("exclude_ids", [])
    if not isinstance(exclude_ids, list):
        exclude_ids = []
    task = context.recommend(max_duration=max_duration, exclude_ids=exclude_ids)
    if task is None:
        return jsonify({"success": False, "error": "No task in this category fits that time. Choose a longer break."}), 422
    category_name = next(category["name"] for category in CATEGORIES if category["id"] == task["category"])
    return jsonify({"success": True, "task": task, "category_name": category_name})


@app.route('/api/tasks/complete', methods=['POST'])
def complete_task():
    payload = request.get_json(silent=True) or {}
    task = get_task(payload.get("task_id"))
    if task is None:
        return jsonify({"success": False, "error": "Task not found."}), 404

    conn = get_db()
    conn.execute("""
        INSERT INTO task_completions (task_id, category, xp)
        VALUES (?, ?, ?)
    """, (task["id"], task["category"], task["xp"]))
    conn.execute("UPDATE user_data SET points = points + ? WHERE id = 1", (task["xp"],))
    user = conn.execute("SELECT points FROM user_data WHERE id = 1").fetchone()
    conn.commit()
    conn.close()

    return jsonify({"success": True, "earned_xp": task["xp"], "points": user["points"]})


# Rastgele soru API'si
@app.route('/api/challenge/random')
def rastgele_soru():
    secilen_soru = random.choice(sorular)
    return jsonify(secilen_soru)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)

