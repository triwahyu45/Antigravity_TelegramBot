import os, sys, json, socket, struct, base64, urllib.request, psutil, ctypes
from urllib.parse import urlparse
try:
    sys.stdout.reconfigure(encoding='utf-8')
except: pass

user32 = ctypes.windll.user32

def find_ag_hwnd():
    target_hwnd = []
    def enum_cb(hwnd, extra):
        if user32.IsWindowVisible(hwnd):
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value
                if "Antigravity" in title or "Wahyu" in title:
                    target_hwnd.append((hwnd, title))
        return True
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.c_int)
    user32.EnumWindows(WNDENUMPROC(enum_cb), 0)
    return target_hwnd

# Minimize window first
hwnds = find_ag_hwnd()
if hwnds:
    print(f"Minimizing HWND {hwnds[0][0]}...")
    user32.ShowWindow(hwnds[0][0], 6) # SW_MINIMIZE

from antigravity_injector import inject_text_to_antigravity

print("Testing injection while MINIMIZED...")
res = inject_text_to_antigravity("Test injeksi saat window minimized")
print("Injection Result while MINIMIZED:", res)
