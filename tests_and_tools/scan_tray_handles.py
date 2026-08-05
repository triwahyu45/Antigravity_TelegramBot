import win32gui
import win32process
import psutil
import win32con

def scan_handles():
    antigravity_pids = set()
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['name'] and 'antigravity' in proc.info['name'].lower():
                antigravity_pids.add(proc.info['pid'])
        except Exception:
            pass

    print('PIDs:', antigravity_pids)

    def enum_cb(hwnd, lparam):
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid in antigravity_pids:
            title = win32gui.GetWindowText(hwnd)
            cname = win32gui.GetClassName(hwnd)
            visible = win32gui.IsWindowVisible(hwnd)
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
            print(f'HWND: {hwnd} | Title: "{title}" | Class: {cname} | Visible: {visible} | Style: {style}')
        return True

    win32gui.EnumWindows(enum_cb, 0)

if __name__ == "__main__":
    scan_handles()
