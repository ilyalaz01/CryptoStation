import time
import logging
import threading
from app.config import Config
from app.collectors.hardware import get_system_metrics
from app.collectors.market import get_crypto_prices
from app.core.analyzer import analyze_and_alert
from app.core.database import Database
from app.bot_service import TeleBotService

# Configure Root Logger
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("CSTM-Orchestrator")

# Initialize Bot Service globally
bot_service = TeleBotService()

def monitor_loop():
    """
    Background process: Collects data, saves to DB, checks alerts.
    Runs strictly every SCAN_INTERVAL seconds.
    """
    # Initialize separate DB connection for this thread
    db = Database()
    if db.connect():
        db.init_db()
    else:
        logger.error("DB Connection failed in Monitor Loop. Running in volatile mode.")

    logger.info(f"Monitor Loop initialized. Polling Interval: {Config.SCAN_INTERVAL}s")
    
    # Send startup notification
    bot_service.send_alert("🚀 **System Online**\nMonitoring Active. Type `/status` for metrics.")

    while True:
        try:
            # --- DATA INGESTION ---
            hw = get_system_metrics()
            prices = get_crypto_prices(["bitcoin", "ethereum"])
            
            # --- LOGGING ---
            if hw.get('gpu_name'):
                logger.info(f"STATUS | GPU: {hw.get('gpu_temp')}°C | BTC: ${prices.get('bitcoin')}")
            else:
                logger.info(f"STATUS | CPU: {hw.get('cpu_usage')}% | BTC: ${prices.get('bitcoin')}")

            # --- ANALYTICS ---
            # Pass the bot's send_alert method as a callback
            analyze_and_alert(hw, prices, bot_service.send_alert)

            # --- DATA PERSISTENCE ---
            db.save_metrics(
                cpu=hw.get('cpu_usage'),
                ram=hw.get('ram_usage'),
                gpu_temp=hw.get('gpu_temp'),
                btc=prices.get('bitcoin'),
                eth=prices.get('ethereum')
            )

            time.sleep(Config.SCAN_INTERVAL)
            
        except Exception as e:
            logger.error(f"Error in monitor loop: {e}")
            time.sleep(5) # Wait before retry to prevent log spam

def run():
    """Main entry point. Starts threads."""
    # 1. Start Monitoring in a background thread (Daemon)
    monitor_thread = threading.Thread(target=monitor_loop)
    monitor_thread.daemon = True 
    monitor_thread.start()

    # 2. Run Telegram Bot in the main thread (Blocking)
    try:
        bot_service.start()
    except KeyboardInterrupt:
        logger.info("Graceful shutdown initiated.")
    except Exception as e:
        logger.critical(f"Critical System Failure: {e}")

if __name__ == "__main__":
    run()