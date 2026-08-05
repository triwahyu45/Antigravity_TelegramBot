import urllib.request
import json
import os

url = 'https://api.github.com/users/triwahyu45/repos?per_page=100'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})

try:
    with urllib.request.urlopen(req) as resp:
        repos = json.loads(resp.read().decode('utf-8'))
        print(f"Total Repositories Found: {len(repos)}")
        
        web_repos = []
        for r in repos:
            name = r['name']
            lang = r.get('language') or 'Unknown'
            clone_url = r['clone_url']
            desc = r.get('description') or ''
            has_pages = r.get('has_pages', False)
            
            # Deteksi repositori berbasis web (HTML, JavaScript, TypeScript, CSS, Vue, PHP, React, dll)
            is_web = (
                lang.lower() in ['html', 'javascript', 'typescript', 'css', 'vue', 'php', 'blade', 'scss']
                or 'web' in name.lower()
                or 'web' in desc.lower()
                or 'site' in name.lower()
                or has_pages
            )
            
            if is_web:
                web_repos.append((name, lang, clone_url))
                print(f"[WEB REPO] {name} | Lang: {lang} | URL: {clone_url}")
            else:
                print(f"[OTHER REPO] {name} | Lang: {lang}")
                
        print(f"\nTotal Web Repositories to Clone: {len(web_repos)}")
        
        target_dir = r"G:\Github TriWahyu45"
        os.makedirs(target_dir, exist_ok=True)
        
        with open(os.path.join(target_dir, "web_repos.json"), "w", encoding="utf-8") as f:
            json.dump(web_repos, f, indent=2)

except Exception as e:
    print(f"Error fetching repos: {e}")
