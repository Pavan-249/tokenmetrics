CREATE TABLE IF NOT EXISTS funding_rates (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(16) NOT NULL,
    rate NUMERIC NOT NULL,
    UNIQUE (timestamp, symbol)
);

CREATE INDEX IF NOT EXISTS idx_funding_rates_symbol_time
ON funding_rates (symbol, timestamp DESC);

SELECT * FROM funding_rates;

SELECT COUNT(*) AS total_keys FROM funding_rates;
SELECT COUNT(*) AS distinct_keys
FROM (
  SELECT DISTINCT timestamp, symbol
  FROM funding_rates
) t;

