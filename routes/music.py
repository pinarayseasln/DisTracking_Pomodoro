from flask import Blueprint, jsonify, request
from database.supabase_client import supabase
from database.db import get_db

music_bp = Blueprint("music", __name__)

USER_ID = 1

PREVIEW_BUCKET = "music-preview"
FULL_BUCKET = "music-full"


# ==========================================
# AMBIENT SOUNDS - PRIVATE SUPABASE STORAGE
# ==========================================

AMBIENT_FILES = {
    "rain": "Rain.mp3",
    "fire": "Fire.mp3",
    "forest": "Enchanted forest.mp3",
    "meditation": "Meditation.mp3",
}


@music_bp.route("/api/music/ambient/<sound_name>", methods=["GET"])
def get_ambient_sound_url():
    sound_name = request.view_args["sound_name"].lower()

    file_name = AMBIENT_FILES.get(sound_name)

    if not file_name:
        return jsonify({
            "success": False,
            "message": "Ambient sound not found."
        }), 404

    try:
        signed = supabase.storage.from_(
            FULL_BUCKET
        ).create_signed_url(file_name, 3600)

        audio_url = (
            signed.get("signedURL")
            or signed.get("signedUrl")
        )

        if not audio_url:
            raise Exception("Could not create signed URL.")

        return jsonify({
            "success": True,
            "audio_url": audio_url
        }), 200

    except Exception as e:
        print(f"Ambient audio error: {e}")

        return jsonify({
            "success": False,
            "message": "Could not load ambient sound."
        }), 500



# ==========================================
# MARKET MUSIC
# ==========================================

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

        excluded_ambient_tracks = {
            "rain",
            "fire",
            "enchanted forest",
            "meditation"
        }

        for track in response.data:
            if track["title"].strip().lower() in excluded_ambient_tracks:
                continue
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


# ==========================================
# PURCHASE MUSIC
# ==========================================

@music_bp.route("/api/music/buy", methods=["POST"])
def buy_music():
    conn = get_db()

    try:
        payload = request.get_json(silent=True) or {}
        track_id = payload.get("track_id")

        if not track_id:
            return jsonify({
                "success": False,
                "message": "Track ID is required."
            }), 400

        track_response = (
            supabase.table("tracks")
            .select("id, title, price, is_active")
            .eq("id", track_id)
            .eq("is_active", True)
            .execute()
        )

        if not track_response.data:
            return jsonify({
                "success": False,
                "message": "Track not found."
            }), 404

        track = track_response.data[0]
        price = int(track["price"])

        existing = (
            supabase.table("purchased_tracks")
            .select("id")
            .eq("user_id", USER_ID)
            .eq("track_id", track_id)
            .execute()
        )

        if existing.data:
            return jsonify({
                "success": False,
                "message": "You already own this track."
            }), 400

        # Deduct points from SQLite
        conn.execute("BEGIN IMMEDIATE")

        result = conn.execute(
            """
            UPDATE user_data
            SET points = points - ?
            WHERE id = ? AND points >= ?
            """,
            (price, USER_ID, price)
        )

        if result.rowcount == 0:
            conn.rollback()

            return jsonify({
                "success": False,
                "message": "Not enough points."
            }), 400

        conn.commit()

        # Register purchase in Supabase
        try:
            supabase.table("purchased_tracks").insert({
                "user_id": USER_ID,
                "track_id": track_id,
                "price_paid": price
            }).execute()

        except Exception:
            # Refund points if Supabase purchase registration fails
            conn.execute(
                "UPDATE user_data SET points = points + ? WHERE id = ?",
                (price, USER_ID)
            )
            conn.commit()
            raise

        user = conn.execute(
            "SELECT points FROM user_data WHERE id = ?",
            (USER_ID,)
        ).fetchone()

        return jsonify({
            "success": True,
            "message": "Track purchased successfully.",
            "track_id": track_id,
            "points": user["points"]
        }), 200

    except Exception as e:
        conn.rollback()
        print(f"Music purchase error: {e}")

        return jsonify({
            "success": False,
            "message": "Could not purchase track."
        }), 500

    finally:
        conn.close()


# ==========================================
# MY MUSIC - OWNED TRACKS
# ==========================================

@music_bp.route("/api/music/library", methods=["GET"])
def get_music_library():
    try:
        purchases = (
            supabase.table("purchased_tracks")
            .select("track_id")
            .eq("user_id", USER_ID)
            .execute()
        )

        track_ids = [item["track_id"] for item in purchases.data]

        if not track_ids:
            return jsonify({"tracks": []}), 200

        response = (
            supabase.table("tracks")
            .select("id, title, artist, audio_path")
            .in_("id", track_ids)
            .execute()
        )

        tracks = []

        for track in response.data:
            signed = supabase.storage.from_(
                FULL_BUCKET
            ).create_signed_url(track["audio_path"], 3600)

            audio_url = (
                signed.get("signedURL")
                or signed.get("signedUrl")
            )

            tracks.append({
                "id": track["id"],
                "title": track["title"],
                "artist": track["artist"],
                "audio_url": audio_url
            })

        return jsonify({"tracks": tracks}), 200

    except Exception as e:
        print(f"Music library error: {e}")
        return jsonify({"error": "Could not load music library"}), 500


# ==========================================
# FAVORITES - OWNED MUSIC ONLY
# ==========================================

@music_bp.route("/api/music/favorites", methods=["GET"])
def get_favorites():
    try:
        response = (
            supabase.table("favorites")
            .select("track_id")
            .eq("user_id", USER_ID)
            .execute()
        )

        return jsonify({
            "favorites": [item["track_id"] for item in response.data]
        }), 200

    except Exception as e:
        print(f"Favorites error: {e}")
        return jsonify({"error": "Could not load favorites"}), 500


@music_bp.route("/api/music/favorites/toggle", methods=["POST"])
def toggle_favorite():
    try:
        payload = request.get_json(silent=True) or {}
        track_id = payload.get("track_id")

        if not track_id:
            return jsonify({
                "success": False,
                "message": "Track ID is required."
            }), 400

        owned = (
            supabase.table("purchased_tracks")
            .select("id")
            .eq("user_id", USER_ID)
            .eq("track_id", track_id)
            .execute()
        )

        if not owned.data:
            return jsonify({
                "success": False,
                "message": "You must own this track first."
            }), 403

        existing = (
            supabase.table("favorites")
            .select("id")
            .eq("user_id", USER_ID)
            .eq("track_id", track_id)
            .execute()
        )

        if existing.data:
            supabase.table("favorites").delete().eq(
                "id", existing.data[0]["id"]
            ).execute()

            return jsonify({
                "success": True,
                "is_favorite": False
            }), 200

        supabase.table("favorites").insert({
            "user_id": USER_ID,
            "track_id": track_id
        }).execute()

        return jsonify({
            "success": True,
            "is_favorite": True
        }), 200

    except Exception as e:
        print(f"Favorite toggle error: {e}")
        return jsonify({
            "success": False,
            "message": "Could not update favorite."
        }), 500


# ==========================================
# WISHLIST - MARKET MUSIC
# ==========================================

@music_bp.route("/api/music/wishlist", methods=["GET"])
def get_wishlist():
    try:
        response = (
            supabase.table("wishlist")
            .select("track_id")
            .eq("user_id", USER_ID)
            .execute()
        )

        return jsonify({
            "wishlist": [item["track_id"] for item in response.data]
        }), 200

    except Exception as e:
        print(f"Wishlist error: {e}")
        return jsonify({"error": "Could not load wishlist"}), 500


@music_bp.route("/api/music/wishlist/toggle", methods=["POST"])
def toggle_wishlist():
    try:
        payload = request.get_json(silent=True) or {}
        track_id = payload.get("track_id")

        if not track_id:
            return jsonify({
                "success": False,
                "message": "Track ID is required."
            }), 400

        existing = (
            supabase.table("wishlist")
            .select("id")
            .eq("user_id", USER_ID)
            .eq("track_id", track_id)
            .execute()
        )

        if existing.data:
            supabase.table("wishlist").delete().eq(
                "id", existing.data[0]["id"]
            ).execute()

            return jsonify({
                "success": True,
                "is_wishlisted": False
            }), 200

        supabase.table("wishlist").insert({
            "user_id": USER_ID,
            "track_id": track_id
        }).execute()

        return jsonify({
            "success": True,
            "is_wishlisted": True
        }), 200

    except Exception as e:
        print(f"Wishlist toggle error: {e}")
        return jsonify({
            "success": False,
            "message": "Could not update wishlist."
        }), 500