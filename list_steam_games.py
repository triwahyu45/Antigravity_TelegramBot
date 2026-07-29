import os
import re

def list_steam_games():
    libraries = [
        r"C:\Program Files (x86)\Steam\steamapps",
        r"E:\SteamLibrary\steamapps"
    ]

    games = []
    for lib in libraries:
        if not os.path.exists(lib):
            continue
        for fname in os.listdir(lib):
            if fname.startswith("appmanifest_") and fname.endswith(".acf"):
                fpath = os.path.join(lib, fname)
                try:
                    content = open(fpath, "r", encoding="utf-8", errors="ignore").read()
                    name_match = re.search(r'"name"\s+"([^"]+)"', content)
                    appid_match = re.search(r'"appid"\s+"([^"]+)"', content)
                    if name_match:
                        game_name = name_match.group(1)
                        appid = appid_match.group(1) if appid_match else "N/A"
                        games.append((game_name, appid, lib))
                except Exception:
                    pass

    if not games:
        print("Tidak ada game Steam yang terdeteksi.")
        return

    print("=== DAFTAR GAME STEAM ===")
    for name, appid, path in sorted(games, key=lambda x: x[0].lower()):
        drive = path[0]  # E.g. 'C' or 'E'
        print(f"- {name} (AppID: {appid}) [Drive {drive}:]")

if __name__ == "__main__":
    list_steam_games()
