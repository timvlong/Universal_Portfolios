# Script for complete pipeline.
# Creates, fills, queries and analyses the database.
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
all_prices = db_access.execute(output_prices_sql).fetchall()
# Converting these lists of prices into NumPy arrays assigned to the stock name in a dictionary.
prices_dict = {stock: np.array(prices) for stock, prices in all_prices}


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
N = 1000
# Calculating the number of stocks being considered.
m = len(stocks)


# Randomly generating N vectors of length m with positive elements that sum to 1.
# Using the Dirichlet distribution to produce a random probability distribution of size m.
# Setting alpha = 1 to ensure a uniform distribution.
alphas = np.ones(m)
portfolios = np.random.dirichlet(alphas, size=N)


# Storing the number of days for which we have price relative data.
days = len(price_rels_dict[stocks[0]])


# Giving each portfolio the same initial wealth of 1.
portfolio_wealths = np.ones(N)
# Storing the wealth of the universal portfolio over time.
up_wealths = []
up_wealth = 1
up_wealths.append(up_wealth)
# Creating the uniform portfolio.
uniform_p = 1/m * np.ones(m)
uniform_p_wealths = []
uniform_p_wealth = 1
uniform_p_wealths.append(uniform_p_wealth)


# Iterating through each day to perform the 'Universal Portfolios' Algorithm.
for i in range(days):
    # Creating an array containing the price relatives on this day for each stock.
    price_rels_day = np.array([price_rels_dict[stock][i] for stock in stocks])
    # Calculating my universal portfolio vector based on this.
    # Weighting the investment into each stock based on the performance of each portfolio.
    # If a portfolio has a larger wealth, you will trust that 'portfolio manager' more and use the stock proportions they did.
    # The @ here represents matrix multiplication.
    up = portfolio_wealths @ portfolios / np.sum(portfolio_wealths)
    # Calculating the factor by which the wealth of this universal portfolio increases.
    # This is equal to the sum of the price relatives of each stock weighted by the proportion of investment into that stock.
    up_wealth *= up @ price_rels_day
    up_wealths.append(up_wealth)
    # Updating the wealth of each portfolio.
    portfolio_wealths *= portfolios @ price_rels_day
    # Storing the wealth of the uniform portfolio for plotting later.
    uniform_p_wealth *= uniform_p @ price_rels_day
    uniform_p_wealths.append(uniform_p_wealth)


# Outputting the performance of the algorithm.
print(f"\n The wealth of the Universal Portfolio algorithm after {days} days was: {up_wealth}. The final portfolio vector was: {up}. \n")


# Finding the best performing constant, rebalanced portfolio with hindsight.
best_crp_idx = np.argmax(portfolio_wealths)
crp = portfolios[best_crp_idx]
print(f"The wealth of the best performing constant, rebalanced portfolio after {days} days was: {portfolio_wealths[best_crp_idx]}. This was obtained with the portfolio vector: {crp}. \n")


# Determining the variation of the best CRP's wealth with time.
crp_wealths = []
crp_wealth = 1
crp_wealths.append(crp_wealth)
for i in range(days):
    # Creating an array containing the price relatives on this day for each stock.
    price_rels_day = np.array([price_rels_dict[stock][i] for stock in stocks])
    # Storing the wealth of the best CRP for plotting later.
    crp_wealth *= crp @ price_rels_day
    crp_wealths.append(crp_wealth)


# Outputting the wealth of the uniform portfolio.
print(f"The wealth of the uniform portfolio after {days} days was: {uniform_p_wealth}. \n")


# Outputting the order of the stocks
print(f"For reference, the order of the stocks in each portfolio is: {stocks}. \n")


# Plotting the variation of wealth for each algorithm.
for i in range(m):
    # Plotting the wealth if we were to invest in singular stocks.
    # These are normalised by their starting price to also begin at 1.
    plt.plot(prices_dict[stocks[i]] / prices_dict[stocks[i]][0], label=stocks[i])
plt.plot(up_wealths, label="Universal Portfolio")
plt.plot(uniform_p_wealths, label="Uniform Portfolio")
plt.plot(crp_wealths, label="Best CRP")
plt.title(f"Wealth Growth Over {days} Days")
plt.xlabel("Day")
plt.ylabel("Wealth (arbitrary units)")
plt.legend()
plt.tight_layout()
plt.show()
