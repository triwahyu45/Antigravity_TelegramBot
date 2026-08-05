"""
Wait-for-IDLE Switcher
- Gunakan pixel color untuk deteksi spinner di samping Wahyu's PC
- Klik HANYA ketika spinner sudah hilang (IDLE state)
"""
import ctypes
import win32gui
import time
from PIL import ImageGrab, Image
import sys

user32 = ctypes.windll.user32

def is_spinner_visible(rect, w, h):
    """
    Screenshot area kecil di samping text 'Wahyu's PC' di sidebar.
    Spinner = pixel terang bergerak. IDLE = pixel gelap solid.
    Cek area: X = 87..120, Y = 295..315 (sekitar ikon spinner kanan nama)
    """
    spin_x1 = rect[0] + int(w * 0.12)
    spin_y1 = rect[1] + int(h * 0.355)
    spin_x2 = rect[0] + int(w * 0.18)
    spin_y2 = rect[1] + int(h * 0.375)

    img = ImageGrab.grab(bbox=(spin_x1, spin_y1, spin_x2, spin_y2), all_screens=True)
    pixels = list(img.getdata())
    
    # Hitung berapa pixel yang "terang" (R > 150 atau G > 150)
    bright = sum(1 for (r,g,b) in pixels if r > 120 or g > 120 or b > 120)
    total = len(pixels)
    ratio = bright / total if total > 0 else 0
    print(f"  [SPINNER CHECK] bright_ratio={ratio:.2f} ({bright}/{total})")
    return ratio > 0.15  # Jika >15% pixel terang = spinner masih ada

def wait_for_idle_and_switch():
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
    if not res:
        print("HWND not found")
        return False
    main_h = res[0]

    user32.keybd_event(0x12, 0, 0, 0)
    user32.SetForegroundWindow(main_h)
    user32.keybd_event(0x12, 0, 2, 0)
    time.sleep(0.3)

    rect = win32gui.GetWindowRect(main_h)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    wahyu_x = rect[0] + int(w * 0.05)
    wahyu_y = rect[1] + int(h * 0.36)

    print("Waiting for IDLE state (spinner disappears)...")
    for attempt in range(60):  # max 60 detik
        rect = win32gui.GetWindowRect(main_h)
        if not is_spinner_visible(rect, w, h):
            print(f"  IDLE detected at attempt {attempt}! Clicking Wahyu's PC...")
            break
        print(f"  Attempt {attempt}: Still BUSY, waiting...")
        time.sleep(1.0)
    
    # Now click
    rect = win32gui.GetWindowRect(main_h)
    w = rect[2] - rect[0]
    h = rect[3] - rect[1]
    wahyu_x = rect[0] + int(w * 0.05)
    wahyu_y = rect[1] + int(h * 0.36)

    user32.SetCursorPos(wahyu_x, wahyu_y)
    time.sleep(0.2)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)
    time.sleep(0.1)
    user32.mouse_event(0x0002, 0, 0, 0, 0)
    time.sleep(0.05)
    user32.mouse_event(0x0004, 0, 0, 0, 0)

    time.sleep(0.8)
    img = ImageGrab.grab(all_screens=True)
    img.save(r"C:\Users\Triwahyu45\.gemini\antigravity\brain\2f289acc-06bd-4e56-b2d3-964240c95268\idle_switch_proof.png")
    print("Click done. Screenshot saved.")
    return True

if __name__ == "__main__":
    wait_for_idle_and_switch()
