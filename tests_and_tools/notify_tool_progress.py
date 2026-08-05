import sys
import os
import re
import telebot

from secrets_loader import BOT_TOKEN, ALLOWED_ID
# ALLOWED_ID imported from secrets_loader

def main():
    if len(sys.argv) < 2:
        return
    text = " ".join(sys.argv[1:]).strip()
    if not text:
        return
    try:
        bot = telebot.TeleBot(BOT_TOKEN)
        bot.send_message(ALLOWED_ID, text, parse_mode="Markdown")
    except Exception:
        try:
            bot = telebot.TeleBot(BOT_TOKEN)
            plain_text = re.sub(r'[\*\_\`#]', '', text)
            bot.send_message(ALLOWED_ID, plain_text, parse_mode=None)
        except Exception:
            pass

if __name__ == "__main__":
    main()
