# Script for complete pipeline.
# Creates, fills, queries and analyses the database.
import duckdb


# Creating our database and connecting to it via db_access.
db_access = duckdb.connect("database.duckdb")


# Creating the tables within the database according to the pre-determined schema.
schema_sql = open("sql/schema.sql", "r").read()
db_access.execute(schema_sql)


# Inserting the financial data into our database.
insert_data_sql = open("sql/insert_data.sql", "r").read()
db_access.execute(insert_data_sql)


# Calculating the price relatives, ie filling the price_relatives table.
calc_returns_sql = open("sql/calc_returns.sql", "r").read()
db_access.execute(calc_returns_sql)


# Printing the raw data table as a pandas DataFrame.
print(db_access.execute("SELECT * FROM raw_daily_info").fetchdf())
# Printing the daily returns table as a pandas DataFrame.
print(db_access.execute("SELECT * FROM price_relatives").fetchdf())