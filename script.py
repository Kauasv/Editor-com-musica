import os
import subprocess
import random

INPUT_FOLDER = "entrada/videos"
MUSIC_FOLDER = "entrada/musicas"
OUTPUT_FOLDER = "saida"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def run(cmd):
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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

def processar(video, musics):
    input_path = os.path.join(INPUT_FOLDER, video)
    base = video.split(".")[0]

    print(f"🎬 Processando: {video}")

    # 1. cortar 15s
    run([
        "ffmpeg", "-y",
        "-i", input_path,
        "-t", "15",
        f"{base}_cut.mp4"
    ])

    # 2. dividir
    run(["ffmpeg", "-y", "-i", f"{base}_cut.mp4", "-ss", "0", "-t", "5", f"{base}_p1.mp4"])
    run(["ffmpeg", "-y", "-i", f"{base}_cut.mp4", "-ss", "5", "-t", "5", f"{base}_p2.mp4"])

    # 3. slow motion
    run([
        "ffmpeg", "-y",
        "-i", f"{base}_p2.mp4",
        "-filter_complex",
        "[0:v]setpts=2.0*PTS[v];[0:a]atempo=0.5[a]",
        "-map", "[v]",
        "-map", "[a]",
        f"{base}_slow.mp4"
    ])

    # 4. reverse
    run([
        "ffmpeg", "-y",
        "-i", f"{base}_slow.mp4",
        "-filter_complex",
        "[0:v]reverse[v];[0:a]areverse[a]",
        "-map", "[v]",
        "-map", "[a]",
        f"{base}_reverse.mp4"
    ])

    # 5. juntar partes
    with open("lista.txt", "w") as f:
        f.write(f"file '{base}_p1.mp4'\n")
        f.write(f"file '{base}_slow.mp4'\n")
        f.write(f"file '{base}_reverse.mp4'\n")

    temp_final = f"{base}_editado.mp4"

    run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", "lista.txt",
        "-c:v", "libx264",
        "-c:a", "aac",
        temp_final
    ])

    # 🎵 6. aplicar música
    music_file = random.choice(musics)
    music_path = os.path.join(MUSIC_FOLDER, music_file)

    duration = get_music_duration(music_path)
    start_time = random.uniform(duration * 0.3, duration * 0.7)

    output_final = os.path.join(
        OUTPUT_FOLDER,
        f"final_{random.randint(1000,9999)}.mp4"
    )

    run([
        "ffmpeg",
        "-y",
        "-ss", str(start_time),
        "-i", music_path,
        "-i", temp_final,
        "-map", "1:v:0",
        "-map", "0:a:0",
        "-c:v", "copy",
        "-shortest",
        output_final
    ])

    # 🧹 limpar arquivos temporários
    arquivos_temp = [
        f"{base}_cut.mp4",
        f"{base}_p1.mp4",
        f"{base}_p2.mp4",
        f"{base}_slow.mp4",
        f"{base}_reverse.mp4",
        temp_final
    ]

    for arq in arquivos_temp:
        if os.path.exists(arq):
            os.remove(arq)

    print(f"✅ Finalizado: {output_final}\n")

def main():
    videos = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".mp4")]
    musics = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith(".mp3")]

    if not videos:
        print("❌ Nenhum vídeo encontrado")
        return

    if not musics:
        print("❌ Nenhuma música encontrada")
        return

    for video in videos:
        processar(video, musics)

if __name__ == "__main__":
    main()