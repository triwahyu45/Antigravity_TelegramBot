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

def robust_open_antigravity():
    ANTIGRAVITY_PATH = r"C:\Users\Triwahyu45\AppData\Local\Programs\antigravity\Antigravity.exe"
    
    # 1. Find existing HWND
    hwnds = find_ag_hwnd()
    if not hwnds:
        print("Launching Antigravity.exe...")
        if os.path.exists(ANTIGRAVITY_PATH):
            subprocess.Popen(f'"{ANTIGRAVITY_PATH}"', shell=True)
            # Loop wait up to 15s for window HWND to appear
            for _ in range(30):
                time.sleep(0.5)
                hwnds = find_ag_hwnd()
                if hwnds: break
        else:
            return False, f"Path tidak ditemukan: {ANTIGRAVITY_PATH}"

    if not hwnds:
        return False, "Gagal menemukan jendela Antigravity setelah dijalankan!"

    hwnd, title = hwnds[0]
    print(f"Restoring & Focusing HWND {hwnd} ({title})...")
    
    # Restore window & bring to front (SW_RESTORE = 9, SW_SHOW = 5)
    user32.ShowWindow(hwnd, 9)
    user32.ShowWindow(hwnd, 5)
    user32.SetForegroundWindow(hwnd)
    
    # Wait for CDP to be ready
    from antigravity_injector import cdp_click_wahyu
    for _ in range(10):
        time.sleep(0.5)
        res = cdp_click_wahyu()
        print("cdp_click_wahyu attempt:", res)
        if res: break
        
    return True, f"Jendela '{title}' Berhasil Dibuka & Tab Wahyu's PC Aktif!"

if __name__ == "__main__":
    ok, note = robust_open_antigravity()
    print("Robust Open Result:", ok, note)
