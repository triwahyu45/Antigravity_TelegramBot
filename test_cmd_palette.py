import ctypes
import win32gui
import time
from PIL import ImageGrab

user32 = ctypes.windll.user32

def set_clipboard_text(text):
    import win32clipboard
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()

def test_command_palette():
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

    print("Pressing Ctrl + Shift + P...")
    user32.keybd_event(0x11, 0, 0, 0)
    user32.keybd_event(0x10, 0, 0, 0)
    user32.keybd_event(0x50, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(0x50, 0, 2, 0)
    user32.keybd_event(0x10, 0, 2, 0)
    user32.keybd_event(0x11, 0, 2, 0)

    time.sleep(0.5)
    img_cp = ImageGrab.grab(all_screens=True)
    img_cp.save(r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\test_cmd_palette.png")

    set_clipboard_text("Wahyu's PC")
    user32.keybd_event(0x11, 0, 0, 0)
    user32.keybd_event(0x56, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(0x56, 0, 2, 0)
    user32.keybd_event(0x11, 0, 2, 0)
    time.sleep(0.3)
    user32.keybd_event(0x0D, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(0x0D, 0, 2, 0)

    time.sleep(1.0)
    img_after = ImageGrab.grab(all_screens=True)
    img_after.save(r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\test_cmd_palette_result.png")
    print("Command palette test completed!")

if __name__ == "__main__":
    test_command_palette()
