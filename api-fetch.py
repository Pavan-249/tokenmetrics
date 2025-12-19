import requests
from datetime import datetime, timezone
import logging
import pandas as pd
from db_write import write_to_db


logging.basicConfig(
    filename="funding_ingestion.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

API_URL = "https://api.hyperliquid.xyz/info"
REQUEST_TIMEOUT = 10


def get_snapshot_time():
    return datetime.now(timezone.utc).replace(
        minute=0, second=0, microsecond=0
    )


def fetch_funding_rates(snapshot_time):
    try:
        payload = {"type": "metaAndAssetCtxs"}
        response = requests.post(API_URL, json=payload, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        data = response.json()

        symbols = data[0]["universe"]
        contexts = data[1]

        records = []

        for i, symbol_info in enumerate(symbols):
            try:
                symbol = symbol_info["name"]
                rate = float(contexts[i]["funding"])
                records.append((snapshot_time, symbol, rate))
            except (KeyError, IndexError, ValueError):
                logging.warning(f"Skipping malformed record at index {i}")

        logging.info(f"Fetched {len(records)} funding rate records")
        return records

    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        return []


def main():
    snapshot_time = get_snapshot_time()
    logging.info(f"Starting ingestion for snapshot_time={snapshot_time.isoformat()}")

    funding_data = fetch_funding_rates(snapshot_time)

    if not funding_data:
        logging.error("No data fetched from API")
        print(
            f"snapshot_time={snapshot_time.isoformat()} | "
            f"records_inserted=0 | errors=1"
        )
        return

    df = pd.DataFrame(
        funding_data,
        columns=["timestamp", "symbol", "rate"]
    )

    write_to_db(df)
    ##Need to add logging here


if __name__ == "__main__":
    main()
