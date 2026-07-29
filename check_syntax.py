import re
import sys

path = r"G:\Github TriWahyu45\GamepadPiano\index.html"
try:
    content = open(path, encoding="utf-8").read()
    scripts = re.findall(r"<script>(.*?)</script>", content, re.DOTALL)
    print(f"Found {len(scripts)} script blocks.")
    for idx, script in enumerate(scripts):
        try:
            compile(script, f"script_{idx}.js", "exec")
            print(f"Script block {idx}: Syntax OK")
        except SyntaxError as se:
            print(f"Script block {idx}: Syntax ERROR!")
            print(f"Line {se.lineno}: {se.text}")
            print(se)
except Exception as e:
    print("Error:", e)
