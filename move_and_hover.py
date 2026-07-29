import ctypes
import time
import sys

user32 = ctypes.windll.user32
sys_path = r"G:\Antigravity_Server\Bot_Scripts"
sys.path.append(sys_path)
from antigravity_injector import get_antigravity_main_hwnd

main_h = get_antigravity_main_hwnd("Wahyu")
if main_h:
    rect = ctypes.wintypes.RECT()
    user32.GetWindowRect(main_h, ctypes.byref(rect))
    left = rect.left
    bottom = rect.bottom
    
    # Coordinates to hover
    click_x = left + 410
    click_y = bottom - 34
    
    user32.ShowWindow(main_h, 9) # SW_RESTORE
    user32.SetForegroundWindow(main_h)
    time.sleep(0.3)
    
    # Move mouse
    user32.SetCursorPos(click_x, click_y)
    print(f"Cursor moved to: ({click_x}, {click_y})")
    
    # Grab screenshot while cursor is hovering
    from PIL import ImageGrab
    path = r"G:\Antigravity_Server\Screenshots\hover_debug.jpg"
    ImageGrab.grab().save(path, "JPEG")
    print("Screenshot saved to:", path)
