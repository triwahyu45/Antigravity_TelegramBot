import ctypes
import win32gui
import time
from PIL import ImageGrab

user32 = ctypes.windll.user32

def test_back():
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

    rect = win32gui.GetWindowRect(main_h)

    # Back arrow coordinate: X = 35, Y = 65
    back_x = rect[0] + 35
    back_y = rect[1] + 65

    print(f"Clicking Back Arrow at ({back_x}, {back_y})...")
    user32.SetCursorPos(back_x, back_y)
    time.sleep(0.1)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)

    time.sleep(1.0)
    img_after = ImageGrab.grab(all_screens=True)
    img_after.save(r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\test_back_arrow_result.png")
    print("Back arrow test completed!")

if __name__ == "__main__":
    test_back()
