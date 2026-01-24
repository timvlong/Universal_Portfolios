-- Inserting data from the .csv files to the database.


-- Adding GameStop data to the table.
INSERT INTO raw_daily_info
SELECT 'GME', date, close, volume
FROM read_csv_auto('data/gme.csv');


-- Adding Nvidia data to the table.
INSERT INTO raw_daily_info
SELECT 'NVDA', date, close, volume
FROM read_csv_auto('data/nvda.csv');