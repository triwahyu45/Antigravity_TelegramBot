import ctypes
import win32gui
import time
from PIL import ImageGrab

user32 = ctypes.windll.user32

def set_foreground(hwnd):
    user32.keybd_event(0x12, 0, 0, 0)
    user32.SetForegroundWindow(hwnd)
    user32.keybd_event(0x12, 0, 2, 0)
    time.sleep(0.5)

def run_nav_test():
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

    rect = win32gui.GetWindowRect(main_h)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]

    # STEP 1: Click + New Conversation (Y = 115)
    x1 = rect[0] + int(w * 0.05)
    y1 = rect[1] + 115
    print(f"[STEP 1] Clicking + New Conversation at ({x1}, {y1})...")
    user32.SetCursorPos(x1, y1)
    time.sleep(0.2)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(1.5)
    img1 = ImageGrab.grab(all_screens=True)
    img1.save(r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\nav_step1_new_conv.png")

    # STEP 2: Click Conversation History (Y = 160)
    x2 = rect[0] + int(w * 0.05)
    y2 = rect[1] + 160
    print(f"[STEP 2] Clicking Conversation History at ({x2}, {y2})...")
    user32.SetCursorPos(x2, y2)
    time.sleep(0.2)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(1.5)
    img2 = ImageGrab.grab(all_screens=True)
    img2.save(r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\nav_step2_conv_history.png")

    # STEP 3: Click Scheduled Tasks (Y = 205)
    x3 = rect[0] + int(w * 0.05)
    y3 = rect[1] + 205
    print(f"[STEP 3] Clicking Scheduled Tasks at ({x3}, {y3})...")
    user32.SetCursorPos(x3, y3)
    time.sleep(0.2)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(1.5)
    img3 = ImageGrab.grab(all_screens=True)
    img3.save(r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\nav_step3_scheduled_tasks.png")

    # STEP 4: Click Wahyu's PC (Y = 364)
    x4 = rect[0] + int(w * 0.05)
    y4 = rect[1] + 364
    print(f"[STEP 4] Clicking Wahyu's PC at ({x4}, {y4})...")
    user32.SetCursorPos(x4, y4)
    time.sleep(0.2)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(1.5)
    img4 = ImageGrab.grab(all_screens=True)
    img4.save(r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\nav_step4_wahyu_pc.png")

    print("Step-by-step navigation test completed successfully!")

if __name__ == "__main__":
    run_nav_test()
