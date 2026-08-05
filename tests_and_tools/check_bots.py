import psutil
bots = ['telegram_bot', 'transcript_mirror', 'antigravity_telegram_bot']
found = []
for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status']):
    try:
        cmd = ' '.join(proc.info['cmdline'] or [])
        for b in bots:
            if b in cmd:
                found.append((b, proc.info['pid'], proc.info['status']))
                print(f"[{proc.info['status'].upper()}] PID={proc.info['pid']} -> {b}")
    except:
        pass

if not found:
    print("TIDAK ADA BOT YANG BERJALAN!")
