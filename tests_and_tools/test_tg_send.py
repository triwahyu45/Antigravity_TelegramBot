import telebot, time
from secrets_loader import BOT_TOKEN, ALLOWED_ID
# ALLOWED_ID imported from secrets_loader
bot = telebot.TeleBot(BOT_TOKEN)
bot.send_message(ALLOWED_ID, "[DOM MIRROR FINAL] Mirror aktif! Pesan baru dari Wahyu's PC akan dikirim ke sini secara otomatis. Test: " + str(int(time.time())))
print("Test message sent to Telegram!")
