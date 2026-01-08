-- Creating the schema, ie the blueprint of the database.


-- Deleting previous 'raw_daily_info' tables to ensure we replace data in our pipline and don't add to it.
DROP TABLE IF EXISTS raw_daily_info;
-- Creating a table to store the close prices and volume of the chosen stock each day.
CREATE TABLE raw_daily_info (
    stock TEXT,
    date DATE,
    -- Setting close prices as floats.
    close DOUBLE,
    -- Setting volume as a large integer, ie no decimals.
    volume BIGINT
);


-- Deleting previous 'price_relatives' tables.
DROP TABLE IF EXISTS price_relatives;
-- Creating a table to store the price relative of each stock, ie the ratio of closing to opening price of the stock.
CREATE TABLE price_relatives (
    stock TEXT,
    date DATE,
    close DOUBLE,
    price_relative DOUBLE
);
