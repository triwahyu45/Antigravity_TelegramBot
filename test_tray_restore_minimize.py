import os, sys, json, socket, struct, base64, urllib.request, psutil, ctypes, subprocess, time
from urllib.parse import urlparse
try:
    sys.stdout.reconfigure(encoding='utf-8')
except: pass

user32 = ctypes.windll.user32

def find_ag_hwnd_all():
    target_hwnd = []
    def enum_cb(hwnd, extra):
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

def is_antigravity_running():
    for p in psutil.process_iter(['name']):
        try:
            if p.info['name'] and 'antigravity' in p.info['name'].lower():
                return True
        except: pass
    return False

def open_antigravity_tray_flow():
    # 1. Check if running
    running = is_antigravity_running()
    print("Is Antigravity Process Running?", running)
    
    hwnds = find_ag_hwnd_all()
    if not hwnds and not running:
        print("Launching Antigravity.exe fresh...")
        ANTIGRAVITY_PATH = r"C:\Users\Triwahyu45\AppData\Local\Programs\antigravity\Antigravity.exe"
        if os.path.exists(ANTIGRAVITY_PATH):
            subprocess.Popen(f'"{ANTIGRAVITY_PATH}"', shell=True)
            for _ in range(20):
                time.sleep(0.5)
                hwnds = find_ag_hwnd_all()
                if hwnds: break
        else:
            return False, "Path Antigravity.exe tidak ditemukan!"

    hwnds = find_ag_hwnd_all()
    if not hwnds:
        # Fallback HWND from process
        return False, "Gagal menemukan jendela Antigravity"

    hwnd, title = hwnds[0]
    print(f"1. Showing window {hwnd} ({title})...")
    user32.ShowWindow(hwnd, 9) # SW_RESTORE
    user32.ShowWindow(hwnd, 5) # SW_SHOW
    user32.SetForegroundWindow(hwnd)
    
    time.sleep(0.3)
    
    print("2. Switching to Wahyu's PC tab via CDP...")
    from antigravity_injector import cdp_click_wahyu
    res = cdp_click_wahyu()
    print("CDP Switch Result:", res)
    
    time.sleep(0.3)
    
    print("3. Minimizing window back to taskbar...")
    user32.ShowWindow(hwnd, 6) # SW_MINIMIZE
    
    return True, f"Jendela '{title}' berhasil dibuka, dipindah ke chat Wahyu's PC, & di-minimize rapi!"

if __name__ == "__main__":
    ok, note = open_antigravity_tray_flow()
    print("Result:", ok, note)
