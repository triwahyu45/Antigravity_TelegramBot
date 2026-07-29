import sys
import os
import re
import telebot

from secrets_loader import BOT_TOKEN, ALLOWED_ID
# ALLOWED_ID imported from secrets_loader

def format_for_telegram(text):
    if not text: return ""
    t = str(text)
    t = re.sub(r'\*\*(.*?)\*\*', r'*\1*', t)
    t = re.sub(r'^#{1,6}\s*(.+)$', r'*\1*', t, flags=re.MULTILINE)
    t = re.sub(r'^\s*[\-\*]\s+', r'• ', t, flags=re.MULTILINE)
    return t

def send_exact(text):
    if not text or not text.strip(): return
    bot = telebot.TeleBot(BOT_TOKEN)
    formatted_text = format_for_telegram(str(text).strip())
    
    lines = formatted_text.splitlines()
    chunks = []
    curr = ""
    for line in lines:
        if len(curr) + len(line) + 1 > 3500:
            if curr: chunks.append(curr)
            curr = line
        else:
            curr = curr + "\n" + line if curr else line
    if curr: chunks.append(curr)

    for chunk in chunks:
        try:
            bot.send_message(ALLOWED_ID, chunk, parse_mode="Markdown")
        except Exception:
            plain_text = re.sub(r'[\*\_\`#]', '', chunk)
            try:
                bot.send_message(ALLOWED_ID, plain_text, parse_mode=None)
            except Exception as e:
                print(f"[EXACT SEND ERR] {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if os.path.exists(arg):
            content = open(arg, encoding="utf-8", errors="ignore").read()
            send_exact(content)
        else:
            send_exact(" ".join(sys.argv[1:]))
