-- Selecting the close prices ordered by the date and grouped by the stock.
-- These will outputted in the main algorithm.py file for manipulation as NumPy arrays.


-- Two columns: stock name and an array containing the close price of each day.
SELECT stock, ARRAY_AGG(close ORDER BY date)
FROM raw_daily_info
GROUP BY stock;