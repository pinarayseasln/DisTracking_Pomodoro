
from flask import Flask, jsonify, render_template
import random
import sqlite3

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


# Rastgele soru API'si
@app.route('/api/challenge/random')
def rastgele_soru():
    secilen_soru = random.choice(sorular)
    return jsonify(secilen_soru)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)

