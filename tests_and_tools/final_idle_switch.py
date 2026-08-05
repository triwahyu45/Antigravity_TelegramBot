import ctypes
import win32gui
import time
from PIL import ImageGrab

user32 = ctypes.windll.user32

def final_switch():
    ctypes.windll.user32.SetProcessDPIAware()
    main_h = None
    def enum_cb(hwnd, res):
        if win32gui.IsWindowVisible(hwnd):
            t = win32gui.GetWindowText(hwnd)
            if "antigravity" in t.lower() or "wahyu" in t.lower():
                res.append(hwnd)
        return True

    res = []
    win32gui.EnumWindows(enum_cb, res)
    if not res: return
    main_h = res[0]
    user32.SetForegroundWindow(main_h)
    time.sleep(0.2)

    rect = win32gui.GetWindowRect(main_h)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]

    wahyu_x = rect[0] + int(w * 0.05)
    wahyu_y = rect[1] + int(h * 0.36)

    print(f"Clicking Wahyu's PC now that task is finished ({wahyu_x}, {wahyu_y})...")
    user32.SetCursorPos(wahyu_x, wahyu_y)
    time.sleep(0.1)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(0.1)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)

    time.sleep(0.8)
    img = ImageGrab.grab(all_screens=True)
    img.save(r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\final_idle_switched_proof.png")

if __name__ == "__main__":
    final_switch()
