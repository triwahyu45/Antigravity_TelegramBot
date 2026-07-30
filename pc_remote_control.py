"""
Google Antigravity Telegram Remote Control Bridge
Full PC Physical Mouse & Keyboard Automation Engine

Author & Original Creator : TriWahyu45 (https://github.com/triwahyu45)
Repository                : https://github.com/triwahyu45/Antigravity_TelegramBot
Copyright (c) 2026 TriWahyu45. All rights reserved.
"""

import win32api, win32con, win32gui, time, ctypes, os, sys

def get_screen_size():
    user32 = ctypes.windll.user32
    user32.SetProcessDPIAware()
    return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)

def mouse_move(x, y):
    try:
        ctypes.windll.user32.SetCursorPos(int(x), int(y))
    except: pass

def mouse_click(x=None, y=None):
    user32 = ctypes.windll.user32
    if x is not None and y is not None:
        try:
            user32.SetCursorPos(int(x), int(y))
        except: pass
        time.sleep(0.1)
    user32.mouse_event(0x0002, 0, 0, 0, 0) # LEFTDOWN
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0) # LEFTUP
    print(f"[REMOTE CONTROL] Mouse Clicked at ({x}, {y})")


def mouse_double_click(x=None, y=None):
    mouse_click(x, y)
    time.sleep(0.1)
    mouse_click()

def mouse_scroll(delta):
    win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, delta, 0)

def send_key_vk(vk):
    win32api.keybd_event(vk, 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(vk, 0, win32con.KEYEVENTF_KEYUP, 0)

def press_enter():
    send_key_vk(0x0D)

def press_space():
    send_key_vk(0x20)

def press_escape():
    send_key_vk(0x1B)

def press_tab():
    send_key_vk(0x09)

def type_text(text):
    for char in text:
        if char == '\n':
            press_enter()
            time.sleep(0.05)
            continue
        vk = win32api.VkKeyScan(char)
        shift = (vk >> 8) & 1
        code = vk & 0xFF
        if shift:
            win32api.keybd_event(0x10, 0, 0, 0) # Shift
        win32api.keybd_event(code, 0, 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(code, 0, win32con.KEYEVENTF_KEYUP, 0)
        if shift:
            win32api.keybd_event(0x10, 0, win32con.KEYEVENTF_KEYUP, 0)

def click_center_play():
    w, h = get_screen_size()
    cx, cy = int(w * 0.5), int(h * 0.45)
    mouse_click(cx, cy)
    print(f"[REMOTE CONTROL] Clicked Video Play Center ({cx}, {cy})")

def click_first_yt_result():
    w, h = get_screen_size()
    # First YouTube search video title thumbnail is located around X=36%, Y=30%
    rx, ry = int(w * 0.36), int(h * 0.30)
    mouse_click(rx, ry)
    time.sleep(0.3)
    press_enter()
    print(f"[REMOTE CONTROL] Clicked & Played First YouTube Result ({rx}, {ry})")


if __name__ == "__main__":
    w, h = get_screen_size()
    print(f"Screen resolution: {w}x{h}")
    print("Testing mouse & keyboard control...")
