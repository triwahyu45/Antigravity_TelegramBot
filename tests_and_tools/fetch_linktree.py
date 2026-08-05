import urllib.request
import re
import json

url = 'https://linktr.ee/triwahyu45'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})

try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode('utf-8')
        
        # Linktree renders links in JSON or html
        urls = re.findall(r'https?://[^\s"<>\'\\]+', html)
        donate_links = set()
        for u in urls:
            u_lower = u.lower()
            if any(k in u_lower for k in ['saweria', 'trakteer', 'dana', 'linktr.ee', 'paypal', 'sociabuzz', 'buymeacoffee']):
                donate_links.add(u)
                
        print("Found Donation / Social Links:")
        for l in sorted(donate_links):
            print(" -", l)

except Exception as e:
    print("Error fetching linktree:", e)
