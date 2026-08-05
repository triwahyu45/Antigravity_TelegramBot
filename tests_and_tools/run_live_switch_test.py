import ctypes
import win32gui
import time
from PIL import ImageGrab

user32 = ctypes.windll.user32

def set_foreground(hwnd):
    user32.ShowWindow(hwnd, 9)
    user32.ShowWindow(hwnd, 3)
    user32.SetForegroundWindow(hwnd)
    user32.keybd_event(0x12, 0, 0, 0)
    user32.keybd_event(0x12, 0, 2, 0)
    user32.SetForegroundWindow(hwnd)

def run_test():
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
    set_foreground(main_h)
    time.sleep(0.3)

    rect = win32gui.GetWindowRect(main_h)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]

    # STEP 1: Click + New Conversation (X=87, Y=115)
    new_x = rect[0] + int(w * 0.05)
    new_y = rect[1] + int(h * 0.12)
    print(f"STEP 1: Clicking + New Conversation at ({new_x}, {new_y})...")
    user32.SetCursorPos(new_x, new_y)
    time.sleep(0.1)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)

    time.sleep(1.2)
    img1 = ImageGrab.grab(all_screens=True)
    img1.save(r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\step1_new_conv.png")

    # STEP 2: Click Wahyu's PC (X=87, Y=364)
    wahyu_x = rect[0] + int(w * 0.05)
    wahyu_y = rect[1] + int(h * 0.36)
    print(f"STEP 2: Clicking Wahyu's PC at ({wahyu_x}, {wahyu_y})...")
    user32.SetCursorPos(wahyu_x, wahyu_y)
    time.sleep(0.1)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(0.1)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)

    time.sleep(1.2)
    img2 = ImageGrab.grab(all_screens=True)
    img2.save(r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\step2_wahyu_pc.png")
    print("Test finished successfully!")

if __name__ == "__main__":
    run_test()
