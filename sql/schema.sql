-- Creating the schema, ie blueprint of the database.


-- Deleting previous 'daily_info' tables to ensure we replace data in our pipline and don't add to it.
DROP TABLE IF EXISTS daily_info;
-- Creating a table to store the close prices and volume of the chosen stock each day.
CREATE TABLE daily_info (
    stock TEXT,
    date DATE,
    -- Setting close prices as floats.
    close DOUBLE,
    -- Setting volume as a large integer, ie no decimals.
    volume BIGINT
);