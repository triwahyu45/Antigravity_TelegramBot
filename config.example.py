import os

# Telegram Bot Credentials
# Replace with your Telegram Bot Token from @BotFather
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")

# Allowed Telegram User ID (numeric chat ID)
ALLOWED_TELEGRAM_ID = int(os.getenv("ALLOWED_TELEGRAM_ID", "123456789"))

# Storage & Folder Paths
BASE_DIR = r"C:\Antigravity_Server"
BOT_SCRIPTS_DIR = os.path.join(BASE_DIR, "Bot_Scripts")
SCREENSHOTS_DIR = os.path.join(BASE_DIR, "Screenshots")
RECEIVED_FILES_DIR = os.path.join(BASE_DIR, "Received_Files")

# Ensure required directories exist
for folder in [BASE_DIR, BOT_SCRIPTS_DIR, SCREENSHOTS_DIR, RECEIVED_FILES_DIR]:
    os.makedirs(folder, exist_ok=True)
