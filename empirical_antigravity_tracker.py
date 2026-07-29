import time
import win32gui
import win32process
import psutil
import ctypes

user32 = ctypes.windll.user32

def force_maximize_and_foreground(hwnd):
    try:
        if user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, 9)
            time.sleep(0.1)
        
        user32.ShowWindow(hwnd, 3)
        time.sleep(0.1)
        user32.SetForegroundWindow(hwnd)
        
        user32.keybd_event(0x12, 0, 0, 0)
        user32.keybd_event(0x12, 0, 2, 0)
        user32.SetForegroundWindow(hwnd)
        time.sleep(0.1)
        
        if not user32.IsZoomed(hwnd):
            user32.ShowWindow(hwnd, 3)
            time.sleep(0.1)
    except Exception as e:
        print(f"[FORCE MAX ERR] {e}")

def track_and_click_wahyu():
    ctypes.windll.user32.SetProcessDPIAware()
    start_t = time.time()
    target_hwnd = None
    target_title = ""
    
    for attempt in range(60):
        res = []
        def enum_cb(hwnd, result):
            if win32gui.IsWindowVisible(hwnd):
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                try:
                    proc = psutil.Process(pid)
                    if 'antigravity' in proc.name().lower():
                        t = win32gui.GetWindowText(hwnd)
                        rect = win32gui.GetWindowRect(hwnd)
                        w = rect[2] - rect[0]
                        h = rect[3] - rect[1]
                        if w > 800 and h > 500:
                            result.append((hwnd, t, proc))
                except Exception:
                    pass
            return True

        win32gui.EnumWindows(enum_cb, res)
        if res:
            target_hwnd, target_title, proc = res[0]
            try:
                cpu = proc.cpu_percent(interval=0.05)
            except Exception:
                cpu = 0.0
            if "wahyu" in target_title.lower() or (time.time() - start_t > 5.0 and cpu < 20.0):
                break
        time.sleep(0.3)

    if not target_hwnd:
        return False, "Jendela Antigravity tidak ditemukan."

    time.sleep(0.8)

    # 1. Maximized & Foreground
    force_maximize_and_foreground(target_hwnd)
    time.sleep(0.3)

    # 2. Eksekusi Klik Presisi Sidebar Wahyu's PC (5% W, 36% H)
    rect = win32gui.GetWindowRect(target_hwnd)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    sidebar_x = rect[0] + int(w * 0.05)
    sidebar_y = rect[1] + int(h * 0.36)

    user32.SetCursorPos(sidebar_x, sidebar_y)
    time.sleep(0.2)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(0.2)
    user32.keybd_event(0x0D, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(0x0D, 0, 2, 0)

    time.sleep(0.3)
    if not user32.IsZoomed(target_hwnd):
        user32.ShowWindow(target_hwnd, 3)

    return True, "Obrolan 'Wahyu's PC' 100% Aktif & Layar Full Maximized!"

if __name__ == "__main__":
    track_and_click_wahyu()
