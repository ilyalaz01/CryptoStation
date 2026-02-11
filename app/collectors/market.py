import requests
import logging
from app.config import Config

# Configure module-level logger
logger = logging.getLogger(__name__)

def get_crypto_prices(coins_list):
    """
    Fetches real-time asset prices via CoinGecko API using a batch request.
    
    Args:
        coins_list (list): List of coin IDs, e.g., ['bitcoin', 'ethereum']
    Returns:
        dict: {'bitcoin': 50000, 'ethereum': 3000}
    """
    if not coins_list:
        return {}

    try:
        # Format list into CSV string for API query
        ids_string = ",".join(coins_list)
        
        params = {
            "ids": ids_string,
            "vs_currencies": "usd"
        }
        
        # Timeout set to 10s to prevent blocking on network lag
        response = requests.get(Config.COINGECKO_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            # Normalize structure: {'bitcoin': {'usd': 50000}} -> {'bitcoin': 50000}
            result = {}
            for coin, price_data in data.items():
                result[coin] = price_data.get('usd')
            return result
            
        elif response.status_code == 429:
            logger.warning("API Rate Limit Exceeded (HTTP 429). Skipping market data update.")
            return {}
        else:
            logger.error(f"Market API returned error {response.status_code}: {response.text}")
            return {}

    except requests.exceptions.RequestException as e:
        logger.error(f"Network Connection Error: {e}")
        return {}