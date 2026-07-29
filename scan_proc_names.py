import psutil

def scan_proc():
    for proc in psutil.process_iter(['pid', 'name', 'exe']):
        try:
            name = proc.info['name'] or ''
            exe = proc.info['exe'] or ''
            if 'antigravity' in name.lower() or 'antigravity' in exe.lower():
                print(f"PID: {proc.info['pid']} | Name: \"{name}\" | Exe: \"{exe}\"")
        except Exception:
            pass

if __name__ == "__main__":
    scan_proc()
