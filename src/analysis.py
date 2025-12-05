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


# Printing the table as a pandas DataFrame.
print(db_access.execute("SELECT * FROM daily_info").fetchdf())