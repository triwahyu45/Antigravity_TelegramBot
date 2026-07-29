import win32gui
import win32process
import psutil
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32

def test_find_window():
    antigravity_pids = set()
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'antigravity' in proc.info['name'].lower():
                antigravity_pids.add(proc.info['pid'])
        except Exception:
            pass

    print("Antigravity PIDs:", antigravity_pids)
    main_candidates = []

    def enum_cb(hwnd, lparam):
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if pid.value in antigravity_pids:
            length = user32.GetWindowTextLengthW(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            user32.GetWindowTextW(hwnd, buff, length + 1)
            title = buff.value
            cname = ctypes.create_unicode_buffer(256)
            user32.GetClassNameW(hwnd, cname, 256)
            visible = user32.IsWindowVisible(hwnd)
            print(f"HWND: {hwnd} | Title: \"{title}\" | Class: {cname.value} | Visible: {visible}")
            if cname.value == "Chrome_WidgetWin_1":
                main_candidates.append((hwnd, title, visible))
        return True

    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
    user32.EnumWindows(WNDENUMPROC(enum_cb), 0)

    print("Main Candidates:", main_candidates)

if __name__ == "__main__":
    test_find_window()
