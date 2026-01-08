-- Inserting data from the .csv files to the database.


-- Adding Apple data to the table.
INSERT INTO raw_daily_info
SELECT 'AAPL', date, close, volume
FROM read_csv_auto('data/aapl.csv');


-- Adding JPMorgan Chase data to the table.
INSERT INTO raw_daily_info
SELECT 'JPM', date, close, volume
FROM read_csv_auto('data/jpm.csv');


-- Adding Coca-Cola data to the table.
INSERT INTO raw_daily_info
SELECT 'KO', date, close, volume
FROM read_csv_auto('data/ko.csv');


-- Adding Tesla data to the table.
INSERT INTO raw_daily_info
SELECT 'TSLA', date, close, volume
FROM read_csv_auto('data/tsla.csv');


-- Adding Walmart data to the table.
INSERT INTO raw_daily_info
SELECT 'WMT', date, close, volume
FROM read_csv_auto('data/wmt.csv');