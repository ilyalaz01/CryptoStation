import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

class Config:
    # URL API
    COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
    
    # ВАЖНО: Ставим 60 секунд, чтобы не ловить ошибку 429
    SCAN_INTERVAL = 60 
    
    # Телеграм (Если не найдено в .env, будет None)
    TG_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TG_CHAT_ID = os.getenv("CHAT_ID")
    
    # Путь к файлу настроек порогов
    SETTINGS_FILE = "config/settings.json"