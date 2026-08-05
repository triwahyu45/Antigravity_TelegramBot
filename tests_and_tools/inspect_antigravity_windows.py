import win32gui
import win32process
import psutil

def inspect():
    def enum_cb(hwnd, result):
        if win32gui.IsWindowVisible(hwnd):
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            try:
                proc = psutil.Process(pid)
                if 'antigravity' in proc.name().lower():
                    title = win32gui.GetWindowText(hwnd)
                    cls = win32gui.GetClassName(hwnd)
                    rect = win32gui.GetWindowRect(hwnd)
                    style = win32gui.GetWindowLong(hwnd, -16)
                    result.append((pid, hwnd, title, cls, rect, style))
            except Exception:
                pass
        return True

    res = []
    win32gui.EnumWindows(enum_cb, res)
    print("Found Antigravity visible windows:")
    for pid, hwnd, title, cls, rect, style in res:
        print(f"PID: {pid} | HWND: {hwnd} | Title: '{title}' | Class: '{cls}' | Rect: {rect} | Style: {hex(style)}")

if __name__ == "__main__":
    inspect()
