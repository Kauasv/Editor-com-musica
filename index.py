import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
import subprocess
import random

# ---------------- CORES ----------------

COR_FUNDO = "#0b0b0b"
COR_SIDEBAR = "#1c1c1c"
COR_CARD = "#121212"

COR_TEXTO = "#ffffff"
COR_SUBTEXTO = "#aaaaaa"

COR_LARANJA = "#ff7a00"
COR_HOVER = "#ff8c1a"
COR_VERDE = "#00d4b3"
COR_AZUL = "#0099cc"

# ---------------- CONFIG ----------------

INPUT_FOLDER = ""
MUSIC_FOLDER = ""
OUTPUT_FOLDER = "saida"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ---------------- FUNÇÕES BACKEND ----------------

def run(cmd):
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def get_music_duration(music_path):
    result = subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration",
         "-of","default=noprint_wrappers=1:nokey=1", music_path],
        stdout=subprocess.PIPE
    )
    return float(result.stdout)

def log(msg):
    log_box.insert(tk.END, msg + "\n")
    log_box.see(tk.END)

def processar(video, musics, total, atual):
    input_path = os.path.join(INPUT_FOLDER, video)
    base = video.split(".")[0]

    log(f"🎬 ({atual}/{total}) Processando: {video}")

    run(["ffmpeg","-y","-i",input_path,"-t","15",f"{base}_cut.mp4"])

    music_file = random.choice(musics)
    music_path = os.path.join(MUSIC_FOLDER, music_file)

    output_final = os.path.join(
        OUTPUT_FOLDER,
        f"final_{random.randint(1000,9999)}.mp4"
    )

    run([
        "ffmpeg","-y",
        "-i", music_path,
        "-i", f"{base}_cut.mp4",
        "-map","1:v:0",
        "-map","0:a:0",
        "-c:v","copy",
        "-shortest",
        output_final
    ])

    if os.path.exists(f"{base}_cut.mp4"):
        os.remove(f"{base}_cut.mp4")

    log(f"✅ Finalizado: {output_final}")

def main_process():
    videos = [f for f in os.listdir(INPUT_FOLDER) if f.endswith(".mp4")]
    musics = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith(".mp3")]

    total = len(videos)

    if not videos or not musics:
        log("❌ Verifique as pastas!")
        return

    for i, video in enumerate(videos, start=1):
        processar(video, musics, total, i)
        progresso['value'] = (i / total) * 100
        janela.update_idletasks()

    log("🎉 FINALIZADO!")
    messagebox.showinfo("Sucesso", "Processamento concluído!")
    os.startfile(OUTPUT_FOLDER)

def iniciar():
    threading.Thread(target=main_process).start()

# ---------------- UI HELPERS ----------------

def criar_botao(parent, texto, cor, hover, cmd):
    btn = tk.Button(
        parent, text=texto, bg=cor, fg="white",
        relief="flat", font=("Segoe UI", 10, "bold"),
        cursor="hand2", command=cmd
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=hover))
    btn.bind("<Leave>", lambda e: btn.config(bg=cor))
    return btn

# ---------------- LOGIN ----------------

def login():
    if user.get() == "admin" and senha.get() == "123":
        login_frame.destroy()
        abrir_sistema()
    else:
        messagebox.showerror("Erro", "Login inválido")

# ---------------- SISTEMA ----------------

def abrir_sistema():
    global log_box, progresso

    # sidebar
    sidebar = tk.Frame(janela, bg=COR_SIDEBAR, width=200)
    sidebar.pack(side="left", fill="y")

    tk.Label(sidebar, text="🎬 Jek360Infinity",
             bg=COR_SIDEBAR, fg=COR_VERDE,
             font=("Segoe UI", 14, "bold")).pack(pady=20)

    criar_botao(sidebar, "Processamento", COR_CARD, COR_VERDE, lambda: None).pack(fill="x", padx=10, pady=5)

    # main
    main = tk.Frame(janela, bg=COR_FUNDO)
    main.pack(expand=True, fill="both")

    tk.Label(main, text="Painel de Controle",
             bg=COR_FUNDO, fg=COR_TEXTO,
             font=("Segoe UI", 16)).pack(pady=10)

    # seleção
    def escolher_videos():
        global INPUT_FOLDER
        INPUT_FOLDER = filedialog.askdirectory()
        lbl_videos.config(text=INPUT_FOLDER)

    def escolher_musicas():
        global MUSIC_FOLDER
        MUSIC_FOLDER = filedialog.askdirectory()
        lbl_musicas.config(text=MUSIC_FOLDER)

    criar_botao(main, "Selecionar Vídeos", COR_AZUL, "#1aa3ff", escolher_videos).pack(pady=5)
    lbl_videos = tk.Label(main, text="Nenhuma pasta", bg=COR_FUNDO, fg=COR_SUBTEXTO)
    lbl_videos.pack()

    criar_botao(main, "Selecionar Músicas", COR_AZUL, "#1aa3ff", escolher_musicas).pack(pady=5)
    lbl_musicas = tk.Label(main, text="Nenhuma pasta", bg=COR_FUNDO, fg=COR_SUBTEXTO)
    lbl_musicas.pack()

    criar_botao(main, "🚀 INICIAR", COR_LARANJA, COR_HOVER, iniciar).pack(pady=10)

    progresso = ttk.Progressbar(main, length=300)
    progresso.pack(pady=10)

    log_box = tk.Text(main, bg="#000000", fg=COR_VERDE, font=("Consolas", 10))
    log_box.pack(expand=True, fill="both", padx=10, pady=10)

# ---------------- JANELA ----------------

janela = tk.Tk()
janela.title("Jek360 Infinity System")
janela.geometry("900x550")
janela.configure(bg=COR_FUNDO)

# login UI
login_frame = tk.Frame(janela, bg=COR_FUNDO)
login_frame.pack(expand=True)

tk.Label(login_frame, text="Login",
         bg=COR_FUNDO, fg=COR_TEXTO,
         font=("Segoe UI", 18)).pack(pady=20)

user = tk.Entry(login_frame)
user.pack(pady=5)

senha = tk.Entry(login_frame, show="*")
senha.pack(pady=5)

criar_botao(login_frame, "Entrar", COR_LARANJA, COR_HOVER, login).pack(pady=10)

janela.mainloop()