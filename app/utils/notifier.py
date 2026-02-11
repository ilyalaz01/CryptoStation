import requests
import logging
from app.config import Config

logger = logging.getLogger(__name__)

def send_telegram_alert(message):
    """
    Dispatches a critical alert via Telegram Bot API.
    Args:
        message (str): Markdown formatted message string.
    """
    if not Config.TG_TOKEN or not Config.TG_CHAT_ID:
        logger.warning("Telegram credentials missing. Alert suppressed.")
        return

    url = f"https://api.telegram.org/bot{Config.TG_TOKEN}/sendMessage"
    payload = {
        "chat_id": Config.TG_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code != 200:
            logger.error(f"Telegram API Error: {response.text}")
    except Exception as e:
        logger.error(f"Failed to dispatch Telegram alert: {e}")