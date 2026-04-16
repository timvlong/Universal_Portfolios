# Script for complete pipeline.
# Creates, fills, queries and analyses the database.
# Implements Thomas Cover's 'Universal Portfolios' algorithm.
import duckdb
import numpy as np
import matplotlib.pyplot as plt


# Creating our database and connecting to it via db_access.
db_access = duckdb.connect("database.duckdb")


# Creating the tables within the database according to the pre-determined schema.
schema_sql = open("sql/schema.sql", "r").read()
db_access.execute(schema_sql)


# Inserting the financial data into our database.
insert_data_sql = open("sql/insert_data.sql", "r").read()
db_access.execute(insert_data_sql)


# Creating a dictionary containing the array of close prices for each stock.
output_prices_sql = open("sql/output_prices.sql", "r").read()
# Storing the stock names, dates and prices.
stock_data = db_access.execute(output_prices_sql).fetchall()
# Converting these lists of prices into NumPy arrays assigned to the stock name in a dictionary.
prices_dict = {stock: np.array(prices) for stock, dates, prices in stock_data}


# Creating a function to output the price relative vector from the vector of close prices.
# This is the vector with element i equal to the close price on day i over the close price on day i-1.
def calc_price_rels(prices):
    """
    Calculating the price relatives based on an array of close prices at each day.

    Parameters
    ----------
    prices (days-dimensional NumPy array): Prices at each day.

    Returns
    -------
    price_rels ((days - 1)-dimensional NumPy array): Price relatives at each day.
    """
    # Calculating the number of days we have prices for.
    days = len(prices)
    # The price relative is undefined on the first day.
    price_rels = np.zeros(days - 1)
    for i in range(days - 1):
        price_rels[i] = prices[i + 1] / prices[i]
    return price_rels


# Creating a dictionary for the price relative vector for each stock.
# Iterating through the key-value pairs in the dictionary using .items() method.
price_rels_dict = {stock: calc_price_rels(prices) for stock, prices in prices_dict.items()}


# Extracting the stock names from the dictionary.
stocks = list(price_rels_dict.keys())


# Setting the number of portfolios to consider.
# This is N in our Monte Carlo approximation of the integral over db.
# Each b is a portfolio vector containing the proportions of the current wealth invested in each of the m stocks.
N = 100000
# Calculating the number of stocks being considered.
m = len(stocks)


# Randomly generating N vectors of length m with positive elements that sum to 1.
# Using the Dirichlet distribution to produce a random probability distribution of size m.
# Setting alpha = 1 to ensure a uniform distribution.
alphas = np.ones(m)
portfolios = np.random.dirichlet(alphas, size=N)


# Storing the number of days for which we have price relative data.
days = len(price_rels_dict[stocks[0]])
# Ensuring we have the same days of data for each stock so they are comparable.
# For instance, can't compare BTC-USD against SPY long-term easily because bitcoin is traded over more days.
for i in range(1, m):
    # Comparing the array of dates of each stock.
    assert stock_data[0][1] == stock_data[i][1], "The data is not compatible. Please adapt the timeframe in consideration or ensure both stocks have data on the same days."
# If this is the case, we may use any of these dates vectors.
dates = stock_data[0][1]
# Determining the beginning and end of the investing period.
start_date = min(dates)
end_date = max(dates)


# Giving each portfolio the same initial wealth of 1.
# Under this assumption, the wealth is equivalent to the wealth relative.
portfolio_wealths = np.ones(N)
# Storing the wealth of the universal portfolio over time.
up_wealths = []
up_wealth = 1
up_wealths.append(up_wealth)
# Storing the universal portfolio vectors over time for plotting later.
up_vectors = []


# Iterating through each day to perform the 'Universal Portfolios' Algorithm.
for i in range(days):
    # Creating an array containing the price relatives on this day for each stock.
    price_rels_day = np.array([price_rels_dict[stock][i] for stock in stocks])
    # Calculating my universal portfolio vector based on this.
    # Weighting the investment into each stock based on the performance of each portfolio.
    # If a portfolio has a larger wealth, you will trust that 'portfolio manager' more and use the stock proportions they did.
    # The @ here represents matrix multiplication.
    up_vector = portfolio_wealths @ portfolios / np.sum(portfolio_wealths)
    # Storing this universal portfolio vector.
    up_vectors.append(up_vector)
    # Calculating the factor by which the wealth of this universal portfolio increases.
    # This is equal to the sum of the price relatives of each stock weighted by the proportion of investment into that stock.
    up_wealth *= up_vector @ price_rels_day
    up_wealths.append(up_wealth)
    # Updating the wealth of each portfolio.
    portfolio_wealths *= portfolios @ price_rels_day


# Outputting the performance of the algorithm.
print(f"\n The wealth of the Universal Portfolio algorithm after {days} days was: {up_wealth}. The final portfolio vector was: {up_vector}. \n")


# Finding the best performing constant, rebalanced portfolio with hindsight.
bcrp_idx = np.argmax(portfolio_wealths)
bcrp_vector = portfolios[bcrp_idx]
print(f"The wealth of the best performing constant, rebalanced portfolio after {days} days was: {portfolio_wealths[bcrp_idx]}. This was obtained with the portfolio vector: {bcrp_vector}. \n")


# Determining the variation of the best CRP's wealth with time.
bcrp_wealths = []
bcrp_wealth = 1
bcrp_wealths.append(bcrp_wealth)
for i in range(days):
    # Creating an array containing the price relatives on this day for each stock.
    price_rels_day = np.array([price_rels_dict[stock][i] for stock in stocks])
    # Storing the wealth of the best CRP for plotting later.
    bcrp_wealth *= bcrp_vector @ price_rels_day
    bcrp_wealths.append(bcrp_wealth)


# Outputting the order of the stocks
print(f"For reference, the order of the stocks in each portfolio is: {stocks}. \n")


# Plotting the variation of wealth and log wealth for each algorithm.
fig, (ax1, ax2) = plt.subplots(1, 2, figsize = (9, 4))
for i in range(m):
    # Plotting the wealth and log wealth if we were to invest in singular stocks.
    # These are normalised by their starting price to also begin at 1.
    ax1.plot(prices_dict[stocks[i]] / prices_dict[stocks[i]][0], label=stocks[i], lw=0.5)
    ax2.plot(np.log(prices_dict[stocks[i]] / prices_dict[stocks[i]][0]), label=stocks[i], lw=0.5)
ax1.plot(up_wealths, label="Universal Portfolio", lw=0.5)
ax2.plot(np.log(up_wealths), label="Universal Portfolio", lw=0.5)
ax1.plot(bcrp_wealths, label="Best CRP", lw=0.5)
ax2.plot(np.log(bcrp_wealths), label="Best CRP", lw=0.5)
fig.suptitle(f"Wealth and Logarithmic Wealth Growth from {start_date} to {end_date}")
ax1.set_xlabel("Day")
ax2.set_xlabel("Day")
ax1.set_ylabel("Wealth (arbitrary units)")
ax2.set_ylabel("Logarithmic Wealth (arbitrary units)")
ax1.grid(linestyle='--', alpha=0.5)
ax2.grid(linestyle='--', alpha=0.5)
ax1.legend()
plt.tight_layout()
plt.show()


# Plotting the variation of the proportion of each stock held in the Universal Portfolio.
# Storing the portfolio vectors over time as an array.
ups_arr = np.array(up_vectors)
# Transposing this array to get m vectors over time, one for each stock.
ups_arr = ups_arr.T
for i in range(m):
    plt.plot(ups_arr[i], label=stocks[i], lw=1)
plt.title(f"Proportion of Stocks Held from {start_date} to {end_date}")
plt.ylabel("Proportion of Wealth")
plt.xlabel("Days")
plt.tight_layout()
plt.grid(linestyle='--', alpha=0.5)
plt.legend()
plt.show()

