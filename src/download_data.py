# Downloading financial data from Yahoo Finance.
import yfinance as yf
import pandas as pd


# Choosing the stocks for consideration.
# Currently testing the results using the S&P500 and Gold.
stocks = ["^GSPC", "GLD"]
for stock in stocks:
    # Downloading the stock prices, in units of the local currency, as a pandas DataFrame.
    data = yf.download(stock, start="2005-01-01", end="2025-01-01")
    # Storing the dates and close prices.
    data = data.reset_index()[["Date", "Close"]]
    # Renaming to align with SQL syntax.
    data.columns = ["date", "close"]
    # Saving the data to a .csv file. Dropping the index column.
    data.to_csv("data/{}.csv".format(stock.lower()), index=False)
