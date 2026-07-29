"""
Google Antigravity Telegram Remote Control Bridge
Windows System Tray Launcher & Indicator Application

Author & Original Creator : TriWahyu45 (https://github.com/triwahyu45)
Repository                : https://github.com/triwahyu45/Antigravity_TelegramBot
Copyright (c) 2026 TriWahyu45. All rights reserved.
"""

import os
import sys
import time
import subprocess
import threading
import psutil
from PIL import Image, ImageDraw, ImageFont
import pystray
from secrets_loader import BOT_TOKEN, ALLOWED_ID

BASE_DIR = r"G:\Antigravity_Server"
SCRIPTS_DIR = os.path.join(BASE_DIR, "Bot_Scripts")

def create_tray_icon_image():
    """Generates a 64x64 sleek futuristic System Tray Icon for Antigravity Bot"""
    img = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Glowing outer circle (Blue-Cyan Gradient feel)
    draw.ellipse((4, 4, 60, 60), fill=(24, 119, 242, 255), outline=(0, 212, 255, 255), width=3)
    # Inner dark circle
    draw.ellipse((12, 12, 52, 52), fill=(15, 23, 42, 255))
    # Glowing A symbol in center
    draw.polygon([(32, 18), (20, 44), (44, 44)], fill=(0, 229, 255, 255))
    draw.line([(24, 36), (40, 36)], fill=(15, 23, 42, 255), width=3)
    # Green active indicator dot in corner
    draw.ellipse((44, 44, 58, 58), fill=(34, 197, 94, 255), outline=(255, 255, 255, 255), width=2)
    return img

def ensure_bot_services_running():
    """Ensures telegram_bot.py and dom_mirror_final.py are active"""
    try:
        ps_check = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-ScheduledTask -TaskName 'AGY_Bot_Receiver' | Select-Object -ExpandProperty State"], capture_output=True, text=True)
        if "Running" not in ps_check.stdout:
            subprocess.run(["powershell", "-NoProfile", "-Command", "Start-ScheduledTask -TaskName 'AGY_Bot_Receiver'"], capture_output=True)
            
        ps_check2 = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-ScheduledTask -TaskName 'AGY_Bot_Mirror' | Select-Object -ExpandProperty State"], capture_output=True, text=True)
        if "Running" not in ps_check2.stdout:
            subprocess.run(["powershell", "-NoProfile", "-Command", "Start-ScheduledTask -TaskName 'AGY_Bot_Mirror'"], capture_output=True)
    except Exception as e:
        print("[TRAY START ERR]", e)

def on_status_clicked(icon, item):
    try:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        icon.notify(f"CPU: {cpu}% | RAM: {ram}%\nReceiver & Mirror Active 🟢", "Antigravity Bot Status")
    except Exception: pass

def on_ss_clicked(icon, item):
    try:
        import telegram_bot as tb
        path = tb.do_screenshot()
        if path:
            icon.notify(f"Screenshot tersimpan: {os.path.basename(path)}", "📸 Screenshot PC Success")
    except Exception as e:
        icon.notify(str(e), "❌ Screenshot Error")

def on_open_antigravity(icon, item):
    try:
        import telegram_bot as tb
        class Dummy:
            chat = type('c', (), {'id': ALLOWED_ID})()
        tb.h_open_antigravity(Dummy())
        icon.notify("Jendela Antigravity dipulihkan di layar PC!", "🖥️ Buka Antigravity")
    except Exception as e: pass

def on_hide_antigravity(icon, item):
    try:
        import telegram_bot as tb
        class Dummy:
            chat = type('c', (), {'id': ALLOWED_ID})()
        tb.h_hide_antigravity(Dummy())
        icon.notify("Antigravity disembunyikan total ke background (SW_HIDE)!", "🙈 Sembunyikan Antigravity")
    except Exception as e: pass

def on_restart_services(icon, item):
    try:
        subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-ScheduledTask -TaskName 'AGY_Bot_Receiver' -ErrorAction SilentlyContinue"], capture_output=True)
        subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-ScheduledTask -TaskName 'AGY_Bot_Mirror' -ErrorAction SilentlyContinue"], capture_output=True)
        time.sleep(1)
        subprocess.run(["powershell", "-NoProfile", "-Command", "Start-ScheduledTask -TaskName 'AGY_Bot_Receiver'"], capture_output=True)
        subprocess.run(["powershell", "-NoProfile", "-Command", "Start-ScheduledTask -TaskName 'AGY_Bot_Mirror'"], capture_output=True)
        icon.notify("Layanan Bot & Mirror berhasil direstart!", "🔄 Restart Services")
    except Exception as e: pass

def on_exit_clicked(icon, item):
    icon.stop()

def run_tray():
    ensure_bot_services_running()
    
    icon_image = create_tray_icon_image()
    menu = pystray.Menu(
        pystray.MenuItem("🟢 Antigravity Bot (Running)", on_status_clicked, default=True),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("📊 Status Server & PC", on_status_clicked),
        pystray.MenuItem("📸 Take PC Screenshot", on_ss_clicked),
        pystray.MenuItem("🖥️ Buka Antigravity", on_open_antigravity),
        pystray.MenuItem("🙈 Sembunyikan Antigravity", on_hide_antigravity),
        pystray.MenuItem("🔄 Restart Bot Services", on_restart_services),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("⚡ Creator: TriWahyu45", lambda i, m: None, enabled=False),
        pystray.MenuItem("❌ Exit System Tray", on_exit_clicked)
    )
    
    icon = pystray.Icon("AntigravityBot", icon_image, "Google Antigravity Bot (Active - Creator: TriWahyu45)", menu)
    print("Starting Antigravity Bot System Tray Icon...")
    icon.run()

if __name__ == "__main__":
    run_tray()
