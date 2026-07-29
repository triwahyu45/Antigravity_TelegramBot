import ctypes
import win32gui
import time
from antigravity_injector import get_antigravity_main_hwnd

user32 = ctypes.windll.user32

def test_switch():
    ctypes.windll.user32.SetProcessDPIAware()
    main_h = get_antigravity_main_hwnd("Wahyu")
    if not main_h:
        print("HWND not found")
        return

    rect = win32gui.GetWindowRect(main_h)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]

    sidebar_x = rect[0] + int(w * 0.05)
    sidebar_y = rect[1] + int(h * 0.36)

    print(f"Clicking X={sidebar_x}, Y={sidebar_y}")
    user32.SetCursorPos(sidebar_x, sidebar_y)
    time.sleep(0.2)
    # Double click
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(0.2)
    
    # Enter key
    user32.keybd_event(0x0D, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(0x0D, 0, 2, 0)
    print("Double click + Enter performed!")

if __name__ == "__main__":
    test_switch()
