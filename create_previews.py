
from pathlib import Path
import subprocess
import sys

# Windows kullanıcı klasörünü otomatik bul
desktop = Path.home() / "OneDrive" / "Masaüstü" / "DisTracking_Music"

# Alternatif olarak normal Masaüstü konumunu kontrol et
if not desktop.exists():
    desktop = Path.home() / "Desktop" / "DisTracking_Music"

full_folder = desktop / "music-full"
preview_folder = desktop / "music-preview"

ffmpeg = (
    Path.home()
    / "AppData/Local/Microsoft/WinGet/Packages/"
    / "Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/"
    / "ffmpeg-9.1-full_build/bin/ffmpeg.exe"
)

if not full_folder.exists():
    sys.exit(f"Music-full klasörü bulunamadı: {full_folder}")

if not ffmpeg.exists():
    sys.exit(f"FFmpeg bulunamadı: {ffmpeg}")

preview_folder.mkdir(parents=True, exist_ok=True)

files = list(full_folder.glob("*.mp3"))

if not files:
    sys.exit("Music-full klasöründe MP3 dosyası bulunamadı.")

print(f"{len(files)} MP3 dosyası bulundu.\n")

for index, source in enumerate(files, start=1):
    destination = preview_folder / source.name

    command = [
        str(ffmpeg),
        "-y",
        "-i", str(source),
        "-t", "25",
        "-vn",
        "-codec:a", "libmp3lame",
        "-b:a", "128k",
        str(destination)
    ]

    print(f"[{index}/{len(files)}] Hazırlanıyor: {source.name}")

    result = subprocess.run(
    command,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.PIPE,
    text=True,
    encoding="utf-8",
    errors="replace"
)

    if result.returncode == 0:
        print("  Tamamlandı!")
    else:
        print(f"  HATA: {result.stderr[-500:]}")

print("\nÖnizleme işlemi tamamlandı!")
print(f"Dosyalar burada: {preview_folder}")
