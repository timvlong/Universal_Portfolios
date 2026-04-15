-- Inserting data from the .csv files to the database.


-- Adding GameStop data to the table.
INSERT INTO raw_daily_info
SELECT '^GSPC', date, close
FROM read_csv_auto('data/^gspc.csv');


-- Adding Nvidia data to the table.
INSERT INTO raw_daily_info
SELECT 'GLD', date, close
FROM read_csv_auto('data/gld.csv');