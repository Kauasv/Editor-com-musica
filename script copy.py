import os
import subprocess
import random

VIDEOS_FOLDER = "entrada/videos"
MUSIC_FOLDER = "entrada/musicas"
OUTPUT_FOLDER = "saida"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

videos = [f for f in os.listdir(VIDEOS_FOLDER) if f.endswith(".mp4")]
musics = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith(".mp3")]

# validação básica
if not videos:
    print("❌ Nenhum vídeo encontrado")
    exit()

if not musics:
    print("❌ Nenhuma música encontrada")
    exit()

def get_music_duration(music_path):
    result = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            music_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return float(result.stdout)

for video in videos:
    video_path = os.path.join(VIDEOS_FOLDER, video)

    # 🎲 sorteia música
    music_file = random.choice(musics)
    music_path = os.path.join(MUSIC_FOLDER, music_file)

    # ⏱ duração da música
    duration = get_music_duration(music_path)

    # 🎵 pega parte aleatória (30% a 70%)
    start_time = random.uniform(duration * 0.3, duration * 0.7)

    # 🎬 nome aleatório
    output_path = os.path.join(
        OUTPUT_FOLDER,
        f"video_{random.randint(1000,9999)}.mp4"
    )
    
    command = [
        "ffmpeg",
        "-y",
        "-ss", str(start_time),
        "-i", music_path,
        "-i", video_path,
        "-map", "1:v:0",   # pega só o vídeo
        "-map", "0:a:0",   # pega só a música
        "-c:v", "copy",
        "-shortest",
        output_path
    ]

    subprocess.run(command)

print("✅ Tudo processado com sucesso!")