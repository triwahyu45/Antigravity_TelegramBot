import os, sys, json, socket, struct, base64, urllib.request, psutil
from urllib.parse import urlparse
try:
    sys.stdout.reconfigure(encoding='utf-8')
except: pass

from antigravity_injector import cdp_click_wahyu

print("Testing cdp_click_wahyu()...")
res = cdp_click_wahyu()
print("cdp_click_wahyu result:", res)
