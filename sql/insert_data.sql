-- Inserting data from the .csv files to the database.

-- Adding Bank of America data to the table.
INSERT INTO raw_daily_info
SELECT 'BAC', date, close
FROM read_csv_auto('data/bac.csv');


-- Adding Ford data to the table.
INSERT INTO raw_daily_info
SELECT 'F', date, close
FROM read_csv_auto('data/f.csv');