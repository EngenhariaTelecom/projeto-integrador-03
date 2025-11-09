#!/usr/bin/env python3
import os
import pty
import tty
import termios
import select
import threading
import time
import random
import errno

# ======== CONFIGURAÇÃO ========
SYMLINK = '/tmp/ttyVIRTUAL'   # será criado apontando para o slave do PTY
BAUD_RATE = 115200            # apenas informativo (PTY não exige config)
BRIDGE_PHYSICAL = False       # se True, tenta abrir /dev/ttyS0 e bridge (veja observação)
PHYSICAL_PORT = '/dev/ttyS0'  # porta física (se BRIDGE_PHYSICAL=True)

V_BATT_MIN = 3.0
V_BATT_MIN_REENABLE = 3.05
V_BATT_MAX = 4.2
V_BATT_MAX_REENABLE = 4.15
CURRENT_NOMINAL = 2.5
OFFSET_CURRENT = 0.05
ADC_NOISE = 0.005
TIMEOUT_USB = 10.0

# ======== ESTADO ========
mode = "MANUAL"
forceCharge = False
forceDischarge = False
v_batt = 3.7
lastSerialTime = time.time()

# ======== Funções de simulação (lógica igual à ESP) ========
def setCharge(on):
    global forceCharge
    forceCharge = on

def setDischarge(on):
    global forceDischarge
    forceDischarge = on

def readBatteryVoltage():
    noise = random.uniform(-ADC_NOISE, ADC_NOISE)
    return v_batt + noise

def readCurrent():
    noise = random.uniform(-ADC_NOISE, ADC_NOISE)
    return CURRENT_NOMINAL + OFFSET_CURRENT + noise

# ======== Cria PTY e link simbólico ========
def create_pty_and_link():
    master_fd, slave_fd = pty.openpty()
    slave_name = os.ttyname(slave_fd)
    # configura raw no slave para comportamento "serial"
    try:
        tty.setraw(slave_fd)
    except Exception:
        pass
    # cria link simbólico (remover antes se existir)
    try:
        if os.path.islink(SYMLINK) or os.path.exists(SYMLINK):
            os.unlink(SYMLINK)
        os.symlink(slave_name, SYMLINK)
    except PermissionError:
        print(f"Aviso: sem permissão para criar {SYMLINK}, usando caminho real {slave_name}")
    except Exception as e:
        print("Aviso criando symlink:", e)
    return master_fd, slave_name

# ======== Escrita/leitura no master_fd ========
def write_master(master_fd, data: bytes):
    total = 0
    while total < len(data):
        try:
            written = os.write(master_fd, data[total:])
            if written == 0:
                raise RuntimeError("write returned 0")
            total += written
        except OSError as e:
            if e.errno == errno.EINTR:
                continue
            print("Erro escrevendo no PTY:", e)
            break

def read_master_nonblock(master_fd, timeout=0.1):
    rlist, _, _ = select.select([master_fd], [], [], timeout)
    if rlist:
        try:
            data = os.read(master_fd, 1024)
            return data
        except OSError as e:
            print("Erro lendo PTY:", e)
            return b''
    return b''

# ======== Handlers de comandos (mesma semântica) ========
def handle_cmd_str(s: str, master_fd):
    global mode, forceCharge, forceDischarge, lastSerialTime
    cmd = s.strip()
    lastSerialTime = time.time()
    print(f"[Serial Received] {cmd}")
    cu = cmd.upper()
    if cu == "AUTO":
        mode = "AUTO"
        write_master(master_fd, b"Modo AUTOMATICO ativado.\n")
    elif cu == "CHARGE ON":
        mode = "MANUAL"
        setCharge(True)
        write_master(master_fd, b"Modo MANUAL: carga FORCADA ON.\n")
    elif cu == "CHARGE OFF":
        mode = "MANUAL"
        setCharge(False)
        write_master(master_fd, b"Modo MANUAL: carga FORCADA OFF.\n")
    elif cu == "DISCH ON":
        mode = "MANUAL"
        setDischarge(True)
        write_master(master_fd, b"Modo MANUAL: descarga FORCADA ON.\n")
    elif cu == "DISCH OFF":
        mode = "MANUAL"
        setDischarge(False)
        write_master(master_fd, b"Modo MANUAL: descarga FORCADA OFF.\n")
    elif cu == "USB ON":
        # só atualiza lastSerialTime
        pass
    else:
        write_master(master_fd, b"Comando invalido.\n")

# ======== Thread que replica a taskCore0 (envia logs e atualiza v_batt) ========
def core0_task(master_fd):
    global v_batt
    while True:
        # Lógica AUTO
        if mode == "AUTO":
            if v_batt <= V_BATT_MIN:
                setDischarge(False)
                setCharge(True)
            elif v_batt >= V_BATT_MAX:
                setCharge(False)
                setDischarge(True)
            elif V_BATT_MIN_REENABLE < v_batt < V_BATT_MAX_REENABLE:
                setCharge(False)
                setDischarge(False)
        else:
            setCharge(forceCharge)
            setDischarge(forceDischarge)

        # Simula variação de tensão
        if forceCharge or (mode == "AUTO" and v_batt <= V_BATT_MIN):
            v_batt += 0.01
            if v_batt > V_BATT_MAX: v_batt = V_BATT_MAX
        elif forceDischarge or (mode == "AUTO" and v_batt >= V_BATT_MAX):
            v_batt -= 0.01
            if v_batt < V_BATT_MIN: v_batt = V_BATT_MIN

        msg = (f"Vbat: {readBatteryVoltage():.3f} V | Mode: {mode} | "
               f"Charge: {'ON' if forceCharge else 'OFF'} | "
               f"Disch: {'ON' if forceDischarge else 'OFF'} | "
               f"Corrente: {readCurrent():.3f} A\n")
        write_master(master_fd, msg.encode('utf-8'))
        time.sleep(0.5)

# ======== Thread que lê dados enviados pelo outro app (aparece no master_fd) ========
def master_reader_task(master_fd):
    buffer = b''
    while True:
        data = read_master_nonblock(master_fd, timeout=0.2)
        if data:
            buffer += data
            # processa por linhas se houver \n
            while b'\n' in buffer:
                line, buffer = buffer.split(b'\n', 1)
                try:
                    s = line.decode('utf-8', errors='ignore')
                except:
                    s = repr(line)
                handle_cmd_str(s, master_fd)
        else:
            # sem dados
            time.sleep(0.05)

# ======== (Opcional) Bridge para porta física ========
def physical_bridge_thread(master_fd):
    # só tenta se BRIDGE_PHYSICAL True
    try:
        import serial
    except Exception:
        print("PySerial não instalado; bridge física desabilitada.")
        return

    try:
        phys = serial.Serial(PHYSICAL_PORT, BAUD_RATE, timeout=0)
        print(f"Bridge: aberto {PHYSICAL_PORT}")
    except Exception as e:
        print("Bridge: não foi possível abrir porta física:", e)
        return

    # forward physical -> master
    def phys_to_master():
        while True:
            try:
                b = phys.read(1024)
                if b:
                    write_master(master_fd, b)
                else:
                    time.sleep(0.01)
            except Exception as e:
                print("Bridge recv error:", e)
                break

    # forward master -> physical
    def master_to_phys():
        while True:
            try:
                data = read_master_nonblock(master_fd, timeout=0.1)
                if data:
                    phys.write(data)
                else:
                    time.sleep(0.01)
            except Exception as e:
                print("Bridge send error:", e)
                break

    threading.Thread(target=phys_to_master, daemon=True).start()
    threading.Thread(target=master_to_phys, daemon=True).start()

# ======== MAIN ========
def main():
    master_fd, slave_name = create_pty_and_link()
    print("PTY criado.")
    print("Use esta porta no seu app (slave):", slave_name)
    if os.path.islink(SYMLINK):
        print("Ou use o link simbólico:", SYMLINK)
    print("O simulador está atuando no lado 'device' do PTY (master).")

    # Inicia threads
    threading.Thread(target=core0_task, args=(master_fd,), daemon=True).start()
    threading.Thread(target=master_reader_task, args=(master_fd,), daemon=True).start()

    if BRIDGE_PHYSICAL:
        threading.Thread(target=physical_bridge_thread, args=(master_fd,), daemon=True).start()

    # Mantém rodando
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Saindo...")

if __name__ == "__main__":
    main()

