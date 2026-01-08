-- Calculating the price relatives of each stock and inserting into the database.


-- Using the raw stock data to calculate the price relatives.
INSERT INTO price_relatives
-- Calculating price relative as ( close(today) / close(yesterday) ).
-- ie factor by which the close price increased from that of yesterday.
SELECT stock, date, close, close / LAG(close) OVER (PARTITION BY stock ORDER BY date) - 1 AS price_relative
FROM raw_daily_info;