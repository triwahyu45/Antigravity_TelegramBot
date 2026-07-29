import ctypes
import win32gui
import time
from PIL import ImageGrab

user32 = ctypes.windll.user32

def guaranteed_switch():
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

    user32.keybd_event(0x12, 0, 0, 0)
    user32.SetForegroundWindow(main_h)
    user32.keybd_event(0x12, 0, 2, 0)
    time.sleep(0.5)

    rect = win32gui.GetWindowRect(main_h)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]

    # STEP 1: Click + New Conversation
    new_x = rect[0] + int(w * 0.05)
    new_y = rect[1] + int(h * 0.12)
    print(f"[STEP 1] Moving mouse to + New Conversation ({new_x}, {new_y})...")
    user32.SetCursorPos(new_x, new_y)
    time.sleep(0.3)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.1)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(1.5)

    img1 = ImageGrab.grab(all_screens=True)
    img1.save(r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\guaranteed_step1_new_conv.png")
    print("Step 1 screenshot saved.")

    # STEP 2: Click Wahyu's PC
    wahyu_x = rect[0] + int(w * 0.05)
    wahyu_y = rect[1] + int(h * 0.36)
    print(f"[STEP 2] Moving mouse to Wahyu's PC ({wahyu_x}, {wahyu_y})...")
    user32.SetCursorPos(wahyu_x, wahyu_y)
    time.sleep(0.3)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.1)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(0.2)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.1)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(1.5)

    img2 = ImageGrab.grab(all_screens=True)
    img2.save(r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\guaranteed_step2_wahyu_pc.png")
    print("Step 2 screenshot saved.")

if __name__ == "__main__":
    guaranteed_switch()
