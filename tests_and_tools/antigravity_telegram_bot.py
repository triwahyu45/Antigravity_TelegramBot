"""
Master Process Manager: Antigravity Telegram Bridge (Multi-Node Architecture)
Menjalankan Node 1 (telegram_bot.py) dan Node 2 (dom_mirror_final.py) secara terpisah & independen.
Single-instance lock mencegah 409 Conflict.
"""
import os
import sys
import time
import subprocess
import psutil

BASE          = r"G:\Antigravity_Server"
BOT_SCRIPT    = os.path.join(BASE, "Bot_Scripts", "telegram_bot.py")
MIRROR_SCRIPT = os.path.join(BASE, "Bot_Scripts", "dom_mirror_final.py")
LOCK_FILE     = os.path.join(BASE, "master.lock")

CREATE_NO_WINDOW = 0x08000000

def check_single_instance():
    if os.path.exists(LOCK_FILE):
        try:
            old_pid = int(open(LOCK_FILE).read().strip())
            if psutil.pid_exists(old_pid):
                print("[MASTER] Killing old instance PID:", old_pid)
                psutil.Process(old_pid).kill()
                time.sleep(1)
        except: pass
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))

def kill_conflicting_bots():
    targets = ['telegram_bot', 'transcript_mirror', 'dom_mirror']
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] == os.getpid(): continue
            cmd = ' '.join(proc.info['cmdline'] or [])
            for t in targets:
                if t in cmd:
                    proc.kill()
                    print("[MASTER] Killed conflicting:", t, "PID=" + str(proc.info['pid']))
                    break
        except: pass
    time.sleep(2)

def start_node(script_path, name):
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUNBUFFERED'] = '1'
    print("[MASTER] Launching '" + name + "':", os.path.basename(script_path))
    return subprocess.Popen(
        [sys.executable, '-u', script_path],
        creationflags=CREATE_NO_WINDOW,
        cwd=os.path.dirname(script_path),
        env=env
    )

def main():
    check_single_instance()
    kill_conflicting_bots()

    print("=====================================================")
    print(" ANTIGRAVITY MULTI-NODE TELEGRAM SERVER STARTED     ")
    print("=====================================================")

    p_bot    = start_node(BOT_SCRIPT,    "Node 1: Bot Receiver")
    p_mirror = start_node(MIRROR_SCRIPT, "Node 2: DOM Mirror")

    while True:
        try:
            if p_bot.poll() is not None:
                print("[MASTER] Node 1 stopped (code " + str(p_bot.returncode) + "). Restarting in 3s...")
                time.sleep(3)
                p_bot = start_node(BOT_SCRIPT, "Node 1: Bot Receiver")

            if p_mirror.poll() is not None:
                print("[MASTER] Node 2 stopped (code " + str(p_mirror.returncode) + "). Restarting in 3s...")
                time.sleep(3)
                p_mirror = start_node(MIRROR_SCRIPT, "Node 2: DOM Mirror")

        except Exception as e:
            print("[MASTER ERR]", e)
        time.sleep(5)

if __name__ == "__main__":
    main()
