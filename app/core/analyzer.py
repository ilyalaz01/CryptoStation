import json
import logging
from app.config import Config

logger = logging.getLogger(__name__)

# State variable to prevent alert flooding
last_alert_state = {}

def load_settings():
    """Loads operational thresholds from JSON configuration."""
    try:
        with open(Config.SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Configuration load failed: {e}")
        return None

def analyze_and_alert(hw_metrics, market_prices, alert_callback):
    """
    Evaluates system metrics against defined thresholds.
    
    Args:
        hw_metrics (dict): Hardware data.
        market_prices (dict): Crypto data.
        alert_callback (func): Function to trigger if alert is needed.
    """
    settings = load_settings()
    if not settings:
        return

    thresholds = settings.get("thresholds", {})
    alerts = []

    # 1. Thermal Analysis (GPU)
    gpu_temp = hw_metrics.get("gpu_temp", 0)
    limit_temp = thresholds.get("gpu_max_temp", 80)
    if gpu_temp > limit_temp:
        alerts.append(f"🔥 **CRITICAL THERMAL EVENT**: GPU at {gpu_temp}°C (Limit: {limit_temp}°C)")

    # 2. Market Analysis (Bitcoin Support Level)
    btc_price = market_prices.get("bitcoin")
    limit_btc = thresholds.get("btc_min_price", 0)
    if btc_price and btc_price < limit_btc:
        alerts.append(f"📉 **MARKET DIP DETECTED**: BTC at ${btc_price} (Target: ${limit_btc})")

    # --- ALERT DISPATCH LOGIC ---
    if alerts:
        full_message = "\n".join(alerts)
        
        # Deduplication logic: Only send if status changed
        global last_alert_state
        if full_message != last_alert_state.get("last_msg"):
            logger.warning(f"Triggering Alert: {full_message}")
            # Execute the callback (send message via Bot)
            alert_callback(f"⚠️ *SYSTEM ALERT*\n\n{full_message}")
            last_alert_state["last_msg"] = full_message
    else:
        # Reset state when system returns to normal
        last_alert_state["last_msg"] = None