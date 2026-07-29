import os
import time
import ctypes
from PIL import ImageGrab

try:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception as e:
    print("DPI awareness error:", e)

# Mouse/Key events
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
KEYEVENTF_KEYUP = 0x0002
VK_M = 0x4D

def click(x, y):
    print(f"Clicking at {x}, {y}...")
    ctypes.windll.user32.SetCursorPos(x, y)
    time.sleep(0.3)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    time.sleep(0.1)
    ctypes.windll.user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(0.2)

def press_key(vk):
    print(f"Pressing key {vk}...")
    ctypes.windll.user32.keybd_event(vk, 0, 0, 0)
    time.sleep(0.05)
    ctypes.windll.user32.keybd_event(vk, 0, KEYEVENTF_KEYUP, 0)

def run_test():
    # 1. Klik ikon Chrome di taskbar (x=558, y=1060)
    click(558, 1060)
    time.sleep(1.5)
    
    # 2. Klik tombol TAP TO START SYSTEM
    click(960, 740)
    time.sleep(2.5)
    
    # 3. Tekan 'm' untuk masuk ke Chord Mode
    press_key(VK_M)
    time.sleep(1.5)
    
    # 4. Ambil screenshot
    screenshot_path = r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\test_screenshot_chord_mode.png"
    print("Taking screenshot of Chord Mode...")
    try:
        img = ImageGrab.grab(all_screens=True)
        img.save(screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")
    except Exception as e:
        print("Error saving screenshot:", e)

if __name__ == "__main__":
    run_test()
