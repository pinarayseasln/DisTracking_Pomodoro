
import random


QUESTIONS = [
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


def get_random_question():
    return random.choice(QUESTIONS)
