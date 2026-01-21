-- Inserting data from the .csv files to the database.


-- Adding Bitcoin USD data to the table.
INSERT INTO raw_daily_info
SELECT 'BTC-USD', date, close, volume
FROM read_csv_auto('data/btc-usd.csv');


-- Adding Ethereum USD data to the table.
INSERT INTO raw_daily_info
SELECT 'ETH-USD', date, close, volume
FROM read_csv_auto('data/eth-usd.csv');