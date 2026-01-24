# Downloading financial data from Yahoo Finance.
import yfinance as yf
import pandas as pd


# Choosing the stocks for consideration.
# The Universal Portfolio algorithm performs best for volatile, uncorrelated stocks.
# Thus we test with NVDA and GameStop. These are volatile and uncorrelated.
stocks = ["NVDA", "GME"]
for stock in stocks:
    # Downloading the stock prices, in units of the local currency, as a pandas DataFrame.
    data = yf.download(stock, start="2020-01-01", end="2025-01-01")
    # Storing the dates, close prices and volume.
    data = data.reset_index()[["Date", "Close", "Volume"]]
    # Renaming to align with SQL syntax.
    data.columns = ["date", "close", "volume"]
    # Saving the data to a .csv file. Dropping the index column.
    data.to_csv("data/{}.csv".format(stock.lower()), index=False)
