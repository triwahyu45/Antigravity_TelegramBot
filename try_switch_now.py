import ctypes
import win32gui
import time
from PIL import ImageGrab

user32 = ctypes.windll.user32

def try_switch():
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
    if not res:
        print("HWND not found")
        return

    main_h = res[0]
    rect = win32gui.GetWindowRect(main_h)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]

    wahyu_x = rect[0] + int(w * 0.05)
    wahyu_y = rect[1] + int(h * 0.36)

    print(f"Clicking Wahyu's PC at ({wahyu_x}, {wahyu_y})...")
    user32.SetCursorPos(wahyu_x, wahyu_y)
    time.sleep(0.2)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(0.1)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)

    time.sleep(1.0)
    img_after = ImageGrab.grab(all_screens=True)
    save_path = r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\live_switch_proof.png"
    img_after.save(save_path)
    print("Proof screenshot saved to:", save_path)

if __name__ == "__main__":
    try_switch()
