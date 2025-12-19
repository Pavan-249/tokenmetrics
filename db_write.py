import psycopg
import pandas as pd
import os

def write_to_db(df):
    conn = psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=5432,
        dbname=os.getenv("DB_NAME", "funding_db"),
        user=os.getenv("DB_USER", "pavankumar_s"),
        password=os.getenv("DB_PASSWORD")
    )

    try:
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        records = list(df.itertuples(index=False, name=None))

        insert_sql = """
        INSERT INTO funding_rates (timestamp, symbol, rate)
        VALUES (%s, %s, %s)
        ON CONFLICT (timestamp, symbol) DO NOTHING;
        """

        with conn.cursor() as cur:
            cur.executemany(insert_sql, records)
            inserted = cur.rowcount

        conn.commit()
        return inserted

    finally:
        conn.close()
