import psutil
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        name = proc.info['name'] or ''
        if 'antigravity' in name.lower():
            pid = proc.info['pid']
            cmd = ' '.join(proc.info['cmdline'] or [])
            print(f"PID={pid}")
            print(f"CMD={cmd}")
            print()
    except Exception as e:
        pass
