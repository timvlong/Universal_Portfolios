-- Inserting data from the .csv files to the database.


-- Adding Nvidia data to the table.
INSERT INTO daily_info
SELECT 'NVDA', date, close, volume
FROM read_csv_auto('data/nvda.csv');


-- Adding Microsoft data to the table.
INSERT INTO daily_info
SELECT 'MSFT', date, close, volume
FROM read_csv_auto('data/msft.csv');


-- Adding Apple data to the table.
INSERT INTO daily_info
SELECT 'AAPL', date, close, volume
FROM read_csv_auto('data/aapl.csv');