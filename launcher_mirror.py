"""
launcher_mirror.py - Launch dom_mirror_final sebagai detached daemon
"""
import subprocess, sys, os, time

LOG_OUT = r"G:\Antigravity_Server\dom_mirror_out.log"
LOG_ERR = r"G:\Antigravity_Server\dom_mirror_err.log"
SCRIPT  = r"G:\Antigravity_Server\Bot_Scripts\dom_mirror_final.py"

# Kill existing mirror processes
import psutil
for p in psutil.process_iter(['pid','name','cmdline']):
    try:
        cmd = ' '.join(p.info.get('cmdline') or [])
        if 'dom_mirror_final' in cmd and p.info['pid'] != os.getpid():
            p.kill()
            print("Killed old mirror PID:", p.info['pid'])
    except: pass

time.sleep(1)

with open(LOG_OUT, 'w') as out, open(LOG_ERR, 'w') as err:
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUNBUFFERED'] = '1'
    proc = subprocess.Popen(
        [sys.executable, '-u', SCRIPT],
        stdout=out, stderr=err,
        env=env,
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
        close_fds=True
    )

print("DOM Mirror started! PID:", proc.pid)
print("Log:", LOG_OUT)
print("Err:", LOG_ERR)
