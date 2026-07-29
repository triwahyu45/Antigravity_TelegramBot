import ctypes
import win32gui
import time
from PIL import ImageGrab

user32 = ctypes.windll.user32

def live_switch_demo():
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

    # STEP 1: Click "+ New Conversation" (X=87, Y=120)
    new_conv_x = rect[0] + int(w * 0.05)
    new_conv_y = rect[1] + int(h * 0.12)
    print(f"[STEP 1] Clicking + New Conversation at ({new_conv_x}, {new_conv_y})...")
    user32.SetCursorPos(new_conv_x, new_conv_y)
    time.sleep(0.2)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    
    time.sleep(1.0)
    img_new = ImageGrab.grab(all_screens=True)
    img_new.save(r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\demo_step1_new_conv.png")

    # STEP 2: Click "Wahyu's PC" (X=87, Y=364)
    wahyu_x = rect[0] + int(w * 0.05)
    wahyu_y = rect[1] + int(h * 0.36)
    print(f"[STEP 2] Clicking Wahyu's PC at ({wahyu_x}, {wahyu_y})...")
    user32.SetCursorPos(wahyu_x, wahyu_y)
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

    time.sleep(1.0)
    img_wahyu = ImageGrab.grab(all_screens=True)
    img_wahyu.save(r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\demo_step2_wahyu_pc.png")
    print("Live switch demo completed!")

if __name__ == "__main__":
    live_switch_demo()
