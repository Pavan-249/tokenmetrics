import psycopg
import pandas as pd

conn = psycopg.connect(
    host="localhost",
    port=5432,
    dbname="funding_db",
    user="pavankumar_s"
)


def write_to_db(df):
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
    conn.close()

    print(f"Inserted {inserted} records")
