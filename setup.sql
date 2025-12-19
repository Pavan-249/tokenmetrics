CREATE DATABASE funding_db;

SELECT current_database();

CREATE TABLE funding_rates (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    symbol VARCHAR(16) NOT NULL,
    rate NUMERIC NOT NULL,
    UNIQUE (timestamp, symbol)
);

INSERT INTO funding_rates (timestamp, symbol, rate)
VALUES ('2025-12-17 10:00:00+00', 'BTC', 0.000125)
ON CONFLICT (timestamp, symbol)z
DO NOTHING;
SELECT * FROM funding_rates;

CREATE INDEX idx_funding_rates_symbol_time
ON funding_rates (symbol, timestamp DESC);


SELECT
  COUNT(*) AS total_keys from funding_rates;

SELECT
  COUNT(*) AS distinct_keys
FROM (
  SELECT DISTINCT timestamp, symbol
  FROM funding_rates
) t;
