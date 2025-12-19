import requests
from datetime import datetime, timezone
import time
import logging
from tokenmetrics.db_write import write_to_db
import pandas as pd

logging.basicConfig(
    filename="funding_ingestion.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

def fetch_funding_rates():
    """Fetch current funding rates from Hyperliquid API.
    
    Returns:
        List of tuples: (timestamp, symbol, rate)
    """
    try:
        payload = {"type": "metaAndAssetCtxs"}
        response = requests.post('https://api.hyperliquid.xyz/info', json=payload, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        # data[0]['universe'] contains symbol metadata
        # data[1] contains funding rates (same order as symbols)
        symbols = data[0]['universe']
        contexts = data[1]
        
        snapshot_time = datetime.now(timezone.utc).replace(
        minute=0, second=0, microsecond=0
        )
        funding_data = []
        
        for i, symbol_info in enumerate(symbols):
            symbol = symbol_info['name']
            rate = float(contexts[i]['funding'])
            funding_data.append((snapshot_time, symbol, rate))
        
        logging.info(f"Fetched funding rates for {len(funding_data)} symbols")
        return funding_data
        
    except requests.exceptions.RequestException as e:
        
        logging.error(f"API request failed: {e}")
        return []
    except (KeyError, IndexError, ValueError) as e:
        print(f"Failed to parse API response: {e}")
        logging.error(f"Failed to parse API response: {e}")
        return []

funding_data = fetch_funding_rates()

df = pd.DataFrame(funding_data, columns=['timestamp', 'symbol', 'rate'])
write_to_db(df)
print(df.head())
