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

def browser_back():
    user32 = ctypes.windll.user32
    # 1. Click top-left Chrome Back Arrow Button (X=25, Y=50)
    try:
        user32.SetCursorPos(25, 50)
        time.sleep(0.05)
        user32.mouse_event(0x0002, 0, 0, 0, 0)
        time.sleep(0.05)
        user32.mouse_event(0x0004, 0, 0, 0, 0)
    except: pass
    time.sleep(0.2)
    # 2. Focus address bar first (Ctrl+L) to prevent YouTube player from receiving Left Arrow key
    send_key_vk(0x11) # Ctrl
    win32api.keybd_event(0x4C, 0, 0, 0) # L
    time.sleep(0.05)
    win32api.keybd_event(0x4C, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(0x11, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(0.1)
    # 3. Send Alt + Left Arrow while address bar is focused
    win32api.keybd_event(win32con.VK_MENU, 0, 0, 0) # Alt
    time.sleep(0.05)
    win32api.keybd_event(win32con.VK_LEFT, 0, 0, 0) # Left Arrow
    time.sleep(0.05)
    win32api.keybd_event(win32con.VK_LEFT, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
    print("[REMOTE CONTROL] Clicked Chrome Back Button & Safe Alt+Left")



def browser_forward():
    win32api.keybd_event(win32con.VK_MENU, 0, 0, 0) # Alt
    time.sleep(0.05)
    win32api.keybd_event(win32con.VK_RIGHT, 0, 0, 0) # Right Arrow
    time.sleep(0.05)
    win32api.keybd_event(win32con.VK_RIGHT, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
    print("[REMOTE CONTROL] Sent Browser Forward (Alt + Right)")


def click_center_play():
    w, h = get_screen_size()
    cx, cy = int(w * 0.5), int(h * 0.45)
    mouse_click(cx, cy)
    print(f"[REMOTE CONTROL] Clicked Video Play Center ({cx}, {cy})")

def click_first_yt_result():
    w, h = get_screen_size()
    # Click YouTube thumbnail image on left (X=24%, Y=28%)
    rx, ry = int(w * 0.24), int(h * 0.28)
    mouse_click(rx, ry)
    time.sleep(0.2)
    # Click YouTube video title text on right (X=36%, Y=28%)
    mouse_click(int(w * 0.36), int(h * 0.28))
    time.sleep(0.3)
    press_enter()
    print(f"[REMOTE CONTROL] Clicked & Played YouTube Thumbnail ({rx}, {ry})")



if __name__ == "__main__":
    w, h = get_screen_size()
    print(f"Screen resolution: {w}x{h}")
    print("Testing mouse & keyboard control...")
