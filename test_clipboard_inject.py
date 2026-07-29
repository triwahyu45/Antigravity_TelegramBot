import win32gui
import win32con
import win32clipboard
import ctypes
import time
from antigravity_injector import get_antigravity_main_hwnd

try:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def set_clipboard(text):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
    win32clipboard.CloseClipboard()

def force_foreground(hwnd):
    try:
        fore_hwnd = user32.GetForegroundWindow()
        if fore_hwnd == hwnd:
            return True
        fore_thread = user32.GetWindowThreadProcessId(fore_hwnd, None)
        curr_thread = kernel32.GetCurrentThreadId()
        user32.AttachThreadInput(curr_thread, fore_thread, True)
        user32.SetForegroundWindow(hwnd)
        user32.AttachThreadInput(curr_thread, fore_thread, False)
        user32.ShowWindow(hwnd, 9)
        return True
    except Exception as e:
        print("Focus error:", e)
        return False

def test_inject(text):
    main_h = get_antigravity_main_hwnd("Wahyu")
    if not main_h:
        print("Main window not found!")
        return

    # Restore if hidden/minimized
    user32.ShowWindow(main_h, 5) # SW_SHOW
    user32.ShowWindow(main_h, 9) # SW_RESTORE
    time.sleep(0.3)
    user32.ShowWindow(main_h, 3) # SW_MAXIMIZE
    time.sleep(0.4)

    force_foreground(main_h)
    user32.keybd_event(0x12, 0, 0, 0)
    user32.keybd_event(0x12, 0, 2, 0)
    time.sleep(0.2)

    # 1. Click input box at (580, 910)
    user32.SetCursorPos(580, 910)
    time.sleep(0.1)
    user32.mouse_event(0x0002, 0, 0, 0, 0) # Down
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0) # Up
    time.sleep(0.2)

    # 2. Set Clipboard
    set_clipboard(text)

    # 3. Paste (Ctrl + V)
    user32.keybd_event(0x11, 0, 0, 0) # Ctrl down
    user32.keybd_event(0x56, 0, 0, 0) # V down
    time.sleep(0.05)
    user32.keybd_event(0x56, 0, 2, 0) # V up
    user32.keybd_event(0x11, 0, 2, 0) # Ctrl up
    time.sleep(0.2)

    # 4. Press Enter
    user32.keybd_event(0x0D, 0, 0, 0) # Enter down
    time.sleep(0.05)
    user32.keybd_event(0x0D, 0, 2, 0) # Enter up

    print("Successfully injected text via Clipboard Paste!")

if __name__ == "__main__":
    test_inject("Tes kirim pesan dari Telegram via Clipboard Paste!")
