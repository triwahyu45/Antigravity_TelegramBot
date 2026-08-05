import os
import subprocess
import json

target_dir = r"G:\Github TriWahyu45"
json_path = os.path.join(target_dir, "web_repos.json")

if not os.path.exists(json_path):
    print("File web_repos.json tidak ditemukan.")
    exit(1)

web_repos = json.load(open(json_path, encoding="utf-8"))
print(f"Mulai cloning {len(web_repos)} repositori web ke {target_dir}...\n")

cloned_count = 0
for name, lang, clone_url in web_repos:
    repo_path = os.path.join(target_dir, name)
    print("=" * 50)
    print(f"Cloning [{name}] ({lang})...")
    print(f"URL: {clone_url}")
    
    if os.path.exists(repo_path):
        print(f"-> Folder {name} sudah ada. Melakukan git pull...")
        cmd = f'git -C "{repo_path}" pull'
    else:
        cmd = f'git clone "{clone_url}" "{repo_path}"'
        
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if r.returncode == 0:
            print(f"[OK] Sukses: {name}")
            cloned_count += 1
        else:
            print(f"[WARN] Error ({r.returncode}): {r.stderr.strip()}")
    except Exception as e:
        print(f"[ERR] Failed: {e}")

print("=" * 50)
print(f"Selesai! Total {cloned_count}/{len(web_repos)} repositori web berhasil di-clone/pull ke {target_dir}.")
