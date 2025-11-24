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
SYMLINK = '/tmp/ttyVIRTUAL'
BAUD_RATE = 115200
BRIDGE_PHYSICAL = False
PHYSICAL_PORT = '/dev/ttyS0'

V_BATT_MIN = 3.0
V_BATT_MAX = 4.2

MANUAL_STEP = 0.01
AUTO_STEP = 0.10

CURRENT_NOMINAL = 2.5
OFFSET_CURRENT = 0.05
ADC_NOISE = 0.005

# ======== ESTADO ========
mode = "MANUAL"
forceCharge = False
forceDischarge = False
v_batt = 3.7


# ======== Funções ========
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


# ======== PTY ========
def create_pty_and_link():
    master_fd, slave_fd = pty.openpty()
    slave_name = os.ttyname(slave_fd)
    try:
        tty.setraw(slave_fd)
    except:
        pass
    try:
        if os.path.islink(SYMLINK) or os.path.exists(SYMLINK):
            os.unlink(SYMLINK)
        os.symlink(slave_name, SYMLINK)
    except:
        pass
    return master_fd, slave_name

def write_master(master_fd, data: bytes):
    try:
        os.write(master_fd, data)
    except:
        pass

def read_master_nonblock(master_fd, timeout=0.1):
    r, _, _ = select.select([master_fd], [], [], timeout)
    if r:
        try:
            return os.read(master_fd, 1024)
        except:
            return b''
    return b''


# ======== COMANDOS ========
def handle_cmd_str(s: str, master_fd):
    global mode, forceCharge, forceDischarge

    cmd = s.strip().upper()

    if cmd == "AUTO":
        mode = "AUTO"

        # AUTO: inicia garantindo carga
        forceCharge = True
        forceDischarge = False

        write_master(master_fd, b"Modo AUTOMATICO ativado.\n")
        return

    if cmd == "CHARGE ON":
        mode = "MANUAL"
        setCharge(True)
        write_master(master_fd, b"Modo MANUAL: carga FORCADA ON.\n")
        return

    if cmd == "CHARGE OFF":
        mode = "MANUAL"
        setCharge(False)
        write_master(master_fd, b"Modo MANUAL: carga FORCADA OFF.\n")
        return

    if cmd == "DISCH ON":
        mode = "MANUAL"
        setDischarge(True)
        write_master(master_fd, b"Modo MANUAL: descarga FORCADA ON.\n")
        return

    if cmd == "DISCH OFF":
        mode = "MANUAL"
        setDischarge(False)
        write_master(master_fd, b"Modo MANUAL: descarga FORCADA OFF.\n")
        return

    write_master(master_fd, b"Comando invalido.\n")


# ======== AUTO + MANUAL SIMULAÇÃO ========
def core0_task(master_fd):
    global v_batt, mode, forceCharge, forceDischarge

    while True:

        # ================================
        #          MODO AUTOMATICO
        # ================================
        if mode == "AUTO":

            # ✔ 1) Se AMBAS ON → só descarga permanece
            if forceCharge and forceDischarge:
                forceCharge = False
                forceDischarge = True

            # ✔ 2) Se NENHUMA ativa → ativa carga
            elif not forceCharge and not forceDischarge:
                forceCharge = True
                forceDischarge = False

            # ✔ 3) Só carga ativa → sobe tensão
            if forceCharge and not forceDischarge:
                v_batt += AUTO_STEP

            # ✔ 4) Só descarga ativa → desce tensão
            elif forceDischarge and not forceCharge:
                v_batt -= AUTO_STEP

        # ================================
        #           MODO MANUAL
        # ================================
        else:
            if forceCharge:
                v_batt += MANUAL_STEP
            elif forceDischarge:
                v_batt -= MANUAL_STEP

        # ======== LIMITES DE SEGURANÇA ========
        if v_batt > V_BATT_MAX:
            v_batt = V_BATT_MAX
            # AUTO: forçar descarga no topo
            if mode == "AUTO":
                forceCharge = False
                forceDischarge = True

        if v_batt < V_BATT_MIN:
            v_batt = V_BATT_MIN
            # AUTO: forçar carga no fundo
            if mode == "AUTO":
                forceCharge = True
                forceDischarge = False

        # Log
        msg = (
            f"Vbat: {readBatteryVoltage():.3f} V | "
            f"Mode: {mode} | "
            f"Charge: {'ON' if forceCharge else 'OFF'} | "
            f"Disch: {'ON' if forceDischarge else 'OFF'} | "
            f"Corrente: {readCurrent():.3f} A\n"
        ).encode()

        write_master(master_fd, msg)
        time.sleep(0.5)


# ======== LEITOR DE COMANDOS ========
def master_reader_task(master_fd):
    buffer = b""
    while True:
        data = read_master_nonblock(master_fd, timeout=0.2)
        if data:
            buffer += data
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                handle_cmd_str(line.decode("utf-8", errors="ignore"), master_fd)
        else:
            time.sleep(0.05)


# ======== MAIN ========
def main():
    master_fd, slave_name = create_pty_and_link()

    print("PTY criado.")
    print("Use esta porta no seu app:", slave_name)
    if os.path.islink(SYMLINK):
        print("Ou use o link simbolico:", SYMLINK)

    threading.Thread(target=core0_task, args=(master_fd,), daemon=True).start()
    threading.Thread(target=master_reader_task, args=(master_fd,), daemon=True).start()

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()