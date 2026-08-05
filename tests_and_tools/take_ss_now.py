import ctypes
import win32gui
from PIL import ImageGrab
import os

def capture_antigravity():
    ctypes.windll.user32.SetProcessDPIAware()
    img = ImageGrab.grab(all_screens=True)
    save_path = r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\test_click_wahyu_pc.png"
    img.save(save_path)
    print("Screenshot saved to:", save_path)

if __name__ == "__main__":
    capture_antigravity()
