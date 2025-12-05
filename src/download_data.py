# Downloading financial data from Yahoo Finance.
import yfinance as yf
import pandas as pd


# Choosing the stock for consideration.
stock = "MSFT"
# Downloading the stock prices, in USD, throughout 2024 as a pandas DataFrame.
data = yf.download(stock, start="2024-01-01", end="2025-01-01")
# Storing the dates, close prices and volume.
data = data.reset_index()[["Date", "Close", "Volume"]]
# Renaming to align with SQL syntax.
data.columns = ["date", "close", "volume"]
# Saving the data to a .csv file. Dropping the index column.
data.to_csv("data/{}.csv".format(stock.lower()), index=False)
