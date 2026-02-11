import telebot
import logging
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import io
from app.config import Config
from app.core.database import Database
from app.collectors.hardware import get_system_metrics
from app.collectors.market import get_crypto_prices

# Set Matplotlib backend to 'Agg' to prevent GUI errors on servers
matplotlib.use('Agg')

logger = logging.getLogger(__name__)

class TeleBotService:
    """
    Manages Telegram Bot interactions (Commands & Alerts).
    Acts as the User Interface for the system.
    """
    def __init__(self):
        if not Config.TG_TOKEN:
            logger.warning("Telegram Token not found in environment variables.")
            return
        
        self.bot = telebot.TeleBot(Config.TG_TOKEN)
        self.db = Database()
        # Note: Database connection is established per request/thread to ensure thread safety.

        # --- COMMAND HANDLERS ---

        @self.bot.message_handler(commands=['start', 'help'])
        def send_welcome(message):
            welcome_text = (
                "🤖 **CryptoStation Commander**\n\n"
                "System is online. Available commands:\n"
                "📊 `/status` - Live system metrics & asset prices\n"
                "📈 `/graph` - Generate 24h GPU thermal chart\n"
                "⚙️ `/config` - Show active thresholds"
            )
            self.bot.reply_to(message, welcome_text, parse_mode="Markdown")

        @self.bot.message_handler(commands=['status'])
        def handle_status(message):
            """Fetch real-time data and reply."""
            self.bot.send_chat_action(message.chat.id, 'typing')
            
            # 1. Fetch live metrics
            hw = get_system_metrics()
            prices = get_crypto_prices(["bitcoin", "ethereum"])
            
            # 2. Format response
            gpu_info = f"{hw.get('gpu_temp')}°C" if hw.get('gpu_name') else "N/A"
            msg = (
                "📊 **Live System Status**\n"
                "--------------------------------\n"
                f"🖥 **CPU:** {hw.get('cpu_usage')}% | **RAM:** {hw.get('ram_usage')}%\n"
                f"🎮 **GPU:** {gpu_info}\n"
                "--------------------------------\n"
                f"💰 **BTC:** ${prices.get('bitcoin', 0):,}\n"
                f"💎 **ETH:** ${prices.get('ethereum', 0):,}"
            )
            self.bot.reply_to(message, msg, parse_mode="Markdown")

        @self.bot.message_handler(commands=['graph'])
        def handle_graph(message):
            """Generate and upload a plot image."""
            self.bot.send_chat_action(message.chat.id, 'upload_photo')
            
            # Connect to DB temporarily
            if not self.db.connect():
                self.bot.reply_to(message, "❌ Database connection failed.")
                return

            try:
                # 1. Query last 1440 records (approx. 24 hours at 1 min interval)
                query = "SELECT timestamp, gpu_temp FROM metrics ORDER BY timestamp DESC LIMIT 1440"
                df = pd.read_sql_query(query, self.db.conn)
                
                if df.empty:
                    self.bot.reply_to(message, "⚠️ No historical data available yet.")
                    return

                # 2. Plotting
                plt.figure(figsize=(10, 5))
                plt.plot(df['timestamp'], df['gpu_temp'], color='tab:red', label='GPU Temp')
                plt.title('GPU Thermal History (Last 24h)')
                plt.xlabel('Time')
                plt.ylabel('Temperature (°C)')
                plt.grid(True, alpha=0.3)
                plt.legend()
                
                # 3. Save to memory buffer
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                plt.close()

                # 4. Send photo
                self.bot.send_photo(message.chat.id, buf, caption="📈 **24h Thermal Analysis**", parse_mode="Markdown")
                
            except Exception as e:
                logger.error(f"Graph generation error: {e}")
                self.bot.reply_to(message, "❌ Error generating graph.")
            finally:
                # Close DB connection to prevent leaks in this thread
                if self.db.conn:
                    self.db.conn.close()

    def start(self):
        """Starts the infinite polling loop."""
        logger.info("Telegram Bot Polling service started.")
        self.bot.infinity_polling()

    def send_alert(self, message):
        """Used by the monitoring loop to push critical alerts."""
        if Config.TG_CHAT_ID:
            try:
                self.bot.send_message(Config.TG_CHAT_ID, message, parse_mode="Markdown")
            except Exception as e:
                logger.error(f"Failed to push alert: {e}")