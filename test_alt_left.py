import ctypes
import win32gui
import time
from PIL import ImageGrab

user32 = ctypes.windll.user32

def test_alt_left():
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

    print("Pressing Alt + Left Arrow...")
    user32.keybd_event(0x12, 0, 0, 0) # Alt down
    user32.keybd_event(0x25, 0, 0, 0) # Left Arrow down
    time.sleep(0.05)
    user32.keybd_event(0x25, 0, 2, 0) # Left Arrow up
    user32.keybd_event(0x12, 0, 2, 0) # Alt up

    time.sleep(1.0)
    img_after = ImageGrab.grab(all_screens=True)
    img_after.save(r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\test_alt_left_result.png")
    print("Alt + Left test completed!")

if __name__ == "__main__":
    test_alt_left()
