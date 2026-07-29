import os, sys, json, socket, struct, base64, urllib.request, psutil, ctypes, subprocess, time
from urllib.parse import urlparse
try:
    sys.stdout.reconfigure(encoding='utf-8')
except: pass

user32 = ctypes.windll.user32

def find_ag_hwnd():
    target_hwnd = []
    def enum_cb(hwnd, extra):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value
                if "Antigravity" in title or "Wahyu" in title:
                    target_hwnd.append((hwnd, title))
        return True
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
    return target_hwnd

def open_or_focus_antigravity():
    hwnds = find_ag_hwnd()
    if hwnds:
        hwnd, title = hwnds[0]
        print(f"Restoring HWND {hwnd} ({title})...")
        user32.ShowWindow(hwnd, 9) # 9 = SW_RESTORE
        user32.SetForegroundWindow(hwnd)
        return True, f"Jendela '{title}' berhasil dipulihkan & difokuskan!"
    
    ANTIGRAVITY_PATH = r"C:\Users\Triwahyu45\AppData\Local\Programs\antigravity\Antigravity.exe"
    if os.path.exists(ANTIGRAVITY_PATH):
        subprocess.Popen(f'"{ANTIGRAVITY_PATH}"', shell=True)
        time.sleep(3)
        return True, "Aplikasi Antigravity IDE baru saja dijalankan!"
    
    return False, "Path Antigravity.exe tidak ditemukan!"

if __name__ == "__main__":
    ok, note = open_or_focus_antigravity()
    print("Open Result:", ok, note)
