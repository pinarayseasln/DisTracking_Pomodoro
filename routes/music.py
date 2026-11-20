
from flask import Blueprint, jsonify
from database.supabase_client import supabase

music_bp = Blueprint("music", __name__)

PREVIEW_BUCKET = "music-preview"


@music_bp.route("/api/music", methods=["GET"])
def get_music():
    try:
        response = (
            supabase.table("tracks")
            .select("id, title, artist, price, preview_path")
            .eq("is_active", True)
            .order("title")
            .execute()
        )

        tracks = []

        for track in response.data:
            preview_url = None

            if track.get("preview_path"):
                preview_url = supabase.storage.from_(
                    PREVIEW_BUCKET
                ).get_public_url(track["preview_path"])

            tracks.append({
                "id": track["id"],
                "title": track["title"],
                "artist": track["artist"],
                "price": track["price"],
                "preview_url": preview_url
            })

        return jsonify(tracks), 200

    except Exception as e:
        print(f"Music API error: {e}")
        return jsonify({"error": "Could not load music"}), 500
