import ctypes
import time
import sys

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32
KEYEVENTF_KEYUP = 0x0002
VK_CONTROL = 0x11
VK_OEM_2 = 0xBF  # '/' key
VK_RETURN = 0x0D
VK_UP = 0x26
VK_DOWN = 0x28

sys.path.append(r"G:\Antigravity_Server\Bot_Scripts")
from antigravity_injector import get_antigravity_main_hwnd

def press_key_slow(vk):
    user32.keybd_event(vk, 0, 0, 0)
    time.sleep(0.05)
    user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.25) # 250ms delay between keys to guarantee Electron registers them

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
        
        user32.ShowWindow(hwnd, 9) # SW_RESTORE
        time.sleep(0.3)
        return user32.GetForegroundWindow() == hwnd
    except Exception as e:
        print(f"[FOCUS ERR] {e}")
        return False

def select_model_by_index_slow(index):
    main_h = get_antigravity_main_hwnd("Wahyu")
    if not main_h:
        print("Main window not found")
        return False

    was_minimized = user32.IsIconic(main_h) or not user32.IsWindowVisible(main_h)
    foreground_hwnd = user32.GetForegroundWindow()

    # 1. Force window focus
    focused = force_foreground(main_h)
    print(f"Force focus status: {focused}")
    time.sleep(0.5)

    # 2. Trigger dropdown: Ctrl + /
    user32.keybd_event(VK_CONTROL, 0, 0, 0)
    time.sleep(0.04)
    user32.keybd_event(VK_OEM_2, 0, 0, 0)
    time.sleep(0.04)
    user32.keybd_event(VK_OEM_2, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(0.04)
    user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)
    time.sleep(1.0) # 1 second wait for dropdown menu to render completely

    # 3. Go to top using UP
    print("Navigating UP...")
    for _ in range(8):
        press_key_slow(VK_UP)
    time.sleep(0.2)

    # 4. Go down to target index
    print(f"Navigating DOWN to index {index}...")
    for _ in range(index):
        press_key_slow(VK_DOWN)
    time.sleep(0.2)

    # 5. Press Enter
    print("Pressing ENTER...")
    press_key_slow(VK_RETURN)
    time.sleep(0.4)

    if was_minimized:
        user32.ShowWindow(main_h, 6) # SW_MINIMIZE
    if foreground_hwnd and foreground_hwnd != main_h:
        force_foreground(foreground_hwnd)

    return True

if __name__ == "__main__":
    idx = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    select_model_by_index_slow(idx)
