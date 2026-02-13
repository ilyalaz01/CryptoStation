import os
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()

class Config:
    # API URL
    COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
    
    # IMPORTANT: Set to 60 seconds to avoid catching a 429 error (rate limit)
    SCAN_INTERVAL = 60 
    
    # Telegram (If not found in .env, it will be None)
    TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TG_CHAT_ID = os.getenv("CHAT_ID")
    
    # Path to the thresholds settings file
    SETTINGS_FILE = "config/settings.json"
