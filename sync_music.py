
from database.supabase_client import supabase
from pathlib import Path

FULL_BUCKET = "music-full"
PREVIEW_BUCKET = "music-preview"
PRICE = 50


def sync_music():
    try:
        # İki bucket'taki dosyaları listele
        full_files = supabase.storage.from_(FULL_BUCKET).list()
        preview_files = supabase.storage.from_(PREVIEW_BUCKET).list()

        full_names = {
            file["name"] for file in full_files
            if file.get("name") and "." in file["name"]
        }

        preview_names = {
            file["name"] for file in preview_files
            if file.get("name") and "." in file["name"]
        }

        print("FULL:", sorted(full_names))
        print("PREVIEW:", sorted(preview_names))

        # Mevcut şarkıları getir
        existing = (
            supabase.table("tracks")
            .select("id, title, audio_path, preview_path")
            .execute()
        )

        existing_paths = {
            track["audio_path"] for track in existing.data
        }

        updated_count = 0
        new_tracks = []

        # Mevcut kayıtların preview_path alanlarını düzelt
        for track in existing.data:
            filename = track["audio_path"]

            if filename in preview_names:
                if track["preview_path"] != filename:
                    supabase.table("tracks").update({
                        "preview_path": filename
                    }).eq("id", track["id"]).execute()

                    updated_count += 1

        # Eksik şarkıları ekle
        for filename in full_names:
            if filename in existing_paths:
                continue

            new_tracks.append({
                "title": Path(filename).stem,
                "artist": "Unknown",
                "audio_path": filename,
                "preview_path": (
                    filename if filename in preview_names else None
                ),
                "price": PRICE,
                "is_active": True
            })

        if new_tracks:
            supabase.table("tracks").insert(new_tracks).execute()

        print(f"{updated_count} şarkının preview_path alanı güncellendi.")
        print(f"{len(new_tracks)} yeni şarkı eklendi.")

    except Exception as e:
        print("Hata:", e)


if __name__ == "__main__":
    sync_music()
