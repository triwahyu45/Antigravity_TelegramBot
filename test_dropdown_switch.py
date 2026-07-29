import ctypes
import win32gui
import time
from PIL import ImageGrab

user32 = ctypes.windll.user32

def test_dropdown():
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
    main_h = res[0]
    user32.SetForegroundWindow(main_h)
    time.sleep(0.2)

    # 1. Toggle Sidebar back on (Ctrl + B)
    user32.keybd_event(0x11, 0, 0, 0)
    user32.keybd_event(0x42, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(0x42, 0, 2, 0)
    user32.keybd_event(0x11, 0, 2, 0)
    time.sleep(0.5)

    rect = win32gui.GetWindowRect(main_h)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]

    drop_x = rect[0] + int(w * 0.38)
    drop_y = rect[1] + int(h * 0.40)

    print(f"Clicking Conversation Dropdown at ({drop_x}, {drop_y})...")
    user32.SetCursorPos(drop_x, drop_y)
    time.sleep(0.2)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)

    time.sleep(0.5)
    user32.keybd_event(0x28, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(0x28, 0, 2, 0)
    time.sleep(0.2)
    user32.keybd_event(0x0D, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(0x0D, 0, 2, 0)

    time.sleep(1.0)
    img_after = ImageGrab.grab(all_screens=True)
    img_after.save(r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\test_dropdown_result.png")
    print("Dropdown test completed!")

if __name__ == "__main__":
    test_dropdown()
