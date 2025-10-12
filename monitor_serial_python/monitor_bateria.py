import tkinter as tk
from tkinter import ttk
import serial
import threading
import time
import csv
import os
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# =========================
# CONFIGURAÇÕES
# =========================
PORTA = 'COM3'         # ex: 'COM3' no Windows ou '/dev/ttyUSB0' no Linux
BAUDRATE = 115200
MAX_PONTOS = 300        # pontos mostrados no gráfico
INTERVALO_ATUALIZACAO = 1000  # ms (1s)
ARQUIVO_CSV = "dados_bateria.csv"

# =========================
# VARIÁVEIS GLOBAIS
# =========================
dados_tensao = deque(maxlen=MAX_PONTOS)
dados_tempo = deque(maxlen=MAX_PONTOS)
modo_atual = "AUTO"
charge_state = "OFF"
disch_state = "OFF"
tempo_inicial = time.time()
rodando = True

# =========================
# CRIA/ABRE CSV
# =========================
def inicializar_csv():
    novo = not os.path.exists(ARQUIVO_CSV)
    with open(ARQUIVO_CSV, "a", newline='') as f:
        writer = csv.writer(f)
        if novo:
            writer.writerow(["Tempo (s)", "Tensao (V)", "Modo", "Carga", "Descarga"])

def salvar_csv(t, v, modo, carga, descarga):
    with open(ARQUIVO_CSV, "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([f"{t:.1f}", f"{v:.3f}", modo, carga, descarga])

inicializar_csv()

# =========================
# FUNÇÕES DE SERIAL
# =========================
def ler_serial():
    global modo_atual, charge_state, disch_state
    while rodando:
        try:
            linha = ser.readline().decode(errors='ignore').strip()
            # LOG:
            print("RAW LINE:", repr(linha))
            if linha.startswith("Vbat:"):
                # Exemplo:
                # Vbat: 3.874 V | Mode: AUTO | Charge: ON | Disch: OFF
                partes = linha.split("|")
                if len(partes) == 4:
                    vbat = float(partes[0].split(":")[1].split("V")[0])
                    modo_atual = partes[1].split(":")[1].strip()
                    charge_state = partes[2].split(":")[1].strip()
                    disch_state = partes[3].split(":")[1].strip()

                    t = time.time() - tempo_inicial
                    dados_tempo.append(t)
                    dados_tensao.append(vbat)

                    # Atualiza labels
                    lbl_vbat.config(text=f"Tensão: {vbat:.3f} V")
                    lbl_mode.config(text=f"Modo: {modo_atual}")
                    lbl_carga.config(text=f"Carga: {charge_state}")
                    lbl_descarga.config(text=f"Descarga: {disch_state}")

                    # Salva no CSV
                    salvar_csv(t, vbat, modo_atual, charge_state, disch_state)

        except Exception:
            pass

# =========================
# FUNÇÕES DE CONTROLE
# =========================
def enviar_comando(cmd):
    ser.write((cmd + "\n").encode())

def start_carga():
    enviar_comando("CHARGE ON")

def stop_carga():
    enviar_comando("CHARGE OFF")

def start_descarga():
    enviar_comando("DISCH ON")

def stop_descarga():
    enviar_comando("DISCH OFF")

def modo_auto():
    enviar_comando("AUTO")

def desligar_tudo():
    global rodando
    # Envia comandos para desligar carga e descarga (HIGH)
    enviar_comando("CHARGE OFF")
    enviar_comando("DISCH OFF")
    time.sleep(0.5)  # espera ESP32 processar
    rodando = False
    try:
        ser.close()
    except:
        pass
    janela.destroy()
    print("Sistema desligado. Dados salvos em", ARQUIVO_CSV)

# =========================
# INTERFACE GRÁFICA
# =========================
janela = tk.Tk()
janela.title("Monitor de Bateria ESP32 + ADS1115")
janela.geometry("720x520")

frame_info = ttk.Frame(janela)
frame_info.pack(pady=10)

lbl_vbat = ttk.Label(frame_info, text="Tensão: -- V", font=("Segoe UI", 14))
lbl_vbat.grid(row=0, column=0, padx=10)

lbl_mode = ttk.Label(frame_info, text="Modo: --", font=("Segoe UI", 12))
lbl_mode.grid(row=1, column=0, padx=10)

lbl_carga = ttk.Label(frame_info, text="Carga: --", font=("Segoe UI", 12))
lbl_carga.grid(row=2, column=0, padx=10)

lbl_descarga = ttk.Label(frame_info, text="Descarga: --", font=("Segoe UI", 12))
lbl_descarga.grid(row=3, column=0, padx=10)

frame_botoes = ttk.Frame(janela)
frame_botoes.pack(pady=10)

ttk.Button(frame_botoes, text="▶️ Start Carga", command=start_carga).grid(row=0, column=0, padx=5)
ttk.Button(frame_botoes, text="⏹ Stop Carga", command=stop_carga).grid(row=0, column=1, padx=5)
ttk.Button(frame_botoes, text="⚡ Start Descarga", command=start_descarga).grid(row=0, column=2, padx=5)
ttk.Button(frame_botoes, text="⏹ Stop Descarga", command=stop_descarga).grid(row=0, column=3, padx=5)
ttk.Button(frame_botoes, text="🤖 Modo AUTO", command=modo_auto).grid(row=0, column=4, padx=5)
ttk.Button(frame_botoes, text="⏹ Desligar Tudo", command=desligar_tudo).grid(row=0, column=5, padx=5)

# =========================
# GRÁFICO
# =========================
fig, ax = plt.subplots(figsize=(6, 3))
line, = ax.plot([], [], color='tab:blue')
ax.set_xlabel("Tempo (s)")
ax.set_ylabel("Tensão (V)")
ax.set_title("Tensão da Bateria em Tempo Real")
ax.grid(True)
plt.tight_layout()

def atualizar_grafico(frame):
    if len(dados_tempo) > 0:
        ax.clear()
        ax.plot(dados_tempo, dados_tensao, color='tab:blue')
        ax.set_xlabel("Tempo (s)")
        ax.set_ylabel("Tensao (V)")
        ax.set_title("Tensao da Bateria em Tempo Real")
        ax.set_ylim(2.5, 4.5)
        ax.grid(True)

ani = FuncAnimation(fig, atualizar_grafico, interval=INTERVALO_ATUALIZACAO)

# =========================
# THREAD SERIAL + INTEGRAÇÃO
# =========================
try:
    ser = serial.Serial(PORTA, BAUDRATE, timeout=1)
    thread_serial = threading.Thread(target=ler_serial, daemon=True)
    thread_serial.start()
except Exception as e:
    print("Erro ao abrir porta serial:", e)
    exit()

# Embute gráfico no Tkinter
canvas = FigureCanvasTkAgg(fig, master=janela)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# =========================
# FINALIZAÇÃO
# =========================
def ao_fechar():
    global rodando
    rodando = False
    try:
        ser.close()
    except:
        pass
    janela.destroy()
    print("Dados salvos em", ARQUIVO_CSV)

janela.protocol("WM_DELETE_WINDOW", ao_fechar)
janela.mainloop()