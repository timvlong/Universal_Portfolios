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
# Calculating the number of stocks being considered.
m = len(stocks)


# Setting the number of portfolios to consider.
# This is N in our Monte Carlo approximation of the integral over db.
# Each b is a portfolio vector containing the proportions of the current wealth invested in each of the m stocks.
num = 100000


# Randomly generating num vectors of length m with positive elements that sum to 1.
# Using the Dirichlet distribution to produce a random probability distribution of size m.
# Setting alpha = 1 to ensure a uniform distribution.
alphas = np.ones(m)
portfolios = np.random.dirichlet(alphas, size=num)


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


# Creating the function that performs Thomas Cover's 'Universal Portfolios' algorithm.
def up_algo(c, num, freq):
    """
    Performs a version of Thomas Cover's 'Universal Portfolios' algorithm adapted to allow for varying transaction costs and rebalancing dates.

    Parameters
    ----------
    c (float): Transaction cost proportionality constant.
    num (integer): Number of 'Portfolio Managers' / portfolios considered in the Monte Carlo approximation.
    freq (integer): Frequency of rebalancing, in days.

    Returns
    -------
    up_wealths (list): Wealth of the Universal portfolio over time.
    up_vectors (list): Universal portfolio vectors over time.
    portfolio_wealths (num-dimensional NumPy array): Final wealth of each of the num portfolios.
    """
    # Setting the initial measure of reallocation to 1, as the portfolio must be built from scratch.
    realloc = 1
    # Giving each portfolio the same initial wealth of 1.
    # Under this assumption, the wealth is equivalent to the wealth relative.
    portfolio_wealths = np.ones(num)
    # Storing the wealth of the Universal portfolio over time.
    up_wealths = []
    # The initial wealth is 1.
    up_wealth = 1
    up_wealths.append(up_wealth)
    # Storing the Universal portfolio vectors over time for plotting later.
    up_vectors = []
    # Setting the initial Universal portfolio.
    up_vector = portfolio_wealths @ portfolios / np.sum(portfolio_wealths)
    up_vectors.append(up_vector)
    # Iterating through each day to perform the 'Universal Portfolios' Algorithm.
    for i in range(days):
        # Creating an array containing the price relatives on this day for each stock.
        price_rels_day = np.array([price_rels_dict[stock][i] for stock in stocks])
        # Calculating the pre-rebalancing portfolio based on the previous Universal portfolio and the current stock market vector.
        # Dividing by the wealth relative to normalise.
        prb_vector = up_vectors[i] * price_rels_day / (up_vectors[i] @ price_rels_day)
        # Updating the wealth of each portfolio.
        portfolio_wealths *= portfolios @ price_rels_day
        # Calculating the factor by which the wealth of this Universal portfolio increases.
        # This is equal to the sum of the price relatives of each stock weighted by the proportion of investment into that stock.
        up_wealth *= (up_vectors[i] @ price_rels_day) * (1 - (c * realloc))
        up_wealths.append(up_wealth)
        # Rebalancing after every 'freq' days.
        # The initialisation of the portfolio counts as the first rebalancing.
        if (i+1) % freq == 0:
            # Calculating my Universal portfolio vector based on this.
            # Weighting the investment into each stock based on the performance of each portfolio.
            # If a portfolio has a larger wealth, you will trust that 'portfolio manager' more and use the stock proportions they did.
            # The @ here represents matrix multiplication.
            up_vector = portfolio_wealths @ portfolios / np.sum(portfolio_wealths)
            # Storing this Universal portfolio vector.
            up_vectors.append(up_vector)
            # Determining the amount of reallocation required to produce the current Universal portfolio.
            realloc = np.abs(prb_vector - up_vector).sum()
        # Continuing with the current portfolio otherwise.
        # No transaction costs in this case.
        else:
            up_vector = prb_vector
            # Storing this Universal portfolio vector.
            up_vectors.append(up_vector)
            # Setting no reallocation.
            realloc = 0
    return up_wealths, up_vectors, portfolio_wealths


# Setting the proportion by which the measure of reallocation impacts the transaction costs.
# Currently set to 10 basis points.
c = 0.001
# Setting the rebalancing frequency in days.
freq = 1


# Performing the algorithm for the chosen parameters.
up_wealths, up_vectors, portfolio_wealths = up_algo(c, num, freq)


# Outputting the performance of the algorithm.
print(f"\nThe wealth of the Universal Portfolio algorithm after {days} days was: {up_wealths[-1]}. The final portfolio vector was: {up_vectors[-1]}. \n")


# Finding the best performing constant, rebalanced portfolio with hindsight.
# This will remain transaction cost free (frictionless) as it becomes too complicated else.
# For instance, upon implementing transaction, the clairvoyant investor with hindsight may choose to rebalance less.
# Furthermore, we'd have to calculate the transaction costs over time of each of the num CRPs to determine which is best.
bcrp_idx = np.argmax(portfolio_wealths)
bcrp_vector = portfolios[bcrp_idx]
# Only fair to compare to the best constant rebalanced portfolio when there are no transactions costs and rebalancing occurs daily.
if c == 0 and freq == 1:
    print(f"The wealth of the best performing constant, rebalanced portfolio after {days} days was: {portfolio_wealths[bcrp_idx]}. This was obtained with the portfolio vector: {bcrp_vector}. \n")


# Determining the variation of the best CRP's wealth with time.
# As no transaction costs are considered, we shall rebalance daily and only compare to the Universal portfolio with no costs and daily rebalancing.
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
    # A transaction cost is requried to build each portfolio but no more after as this is a buy and hold strategy.
    ax1.plot((prices_dict[stocks[i]] * (1 - c)) / prices_dict[stocks[i]][0], label=stocks[i], lw=0.5)
    ax2.plot(np.log((prices_dict[stocks[i]] * (1 - c)) / prices_dict[stocks[i]][0]), label=stocks[i], lw=0.5)
ax1.plot(up_wealths, label="Universal Portfolio", lw=0.5)
ax2.plot(np.log(up_wealths), label="Universal Portfolio", lw=0.5)
# Only fair to compare to the best constant rebalanced portfolio when there are no transactions costs and rebalancing occurs daily.
if c == 0 and freq == 1:
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
plt.xlabel("Day")
plt.tight_layout()
plt.grid(linestyle='--', alpha=0.5)
plt.legend()
plt.show()


# Plotting the variation of the Universal portfolio with the magnitude of the transaction costs.
# Selecting values of c to investigate.
cs = [0, 0.001, 0.01, 0.1]
for c in cs:
    up_wealths, up_vectors, portfolio_wealths = up_algo(c, num, 1)
    plt.plot(up_wealths, label=c, lw=0.5)
plt.title(f"Effect of Transaction Costs on the Universal Portfolio")
plt.xlabel("Day")
plt.ylabel("Wealth (arbitrary units)")
plt.tight_layout()
plt.grid(linestyle='--', alpha=0.5)
plt.legend()
plt.show()


# Plotting the variation of the Universal portfolio with the frequency of rebalancing.
# Selecting values of freq to investigate.
freqs = [1, 100, 1000, 5000]
for freq in freqs:
    up_wealths, up_vectors, portfolio_wealths = up_algo(0.001, num, freq)
    plt.plot(up_wealths, label=freq, lw=0.5)
plt.title(f"Effect of Rebalancing Frequency on the Universal Portfolio")
plt.xlabel("Day")
plt.ylabel("Wealth (arbitrary units)")
plt.tight_layout()
plt.grid(linestyle='--', alpha=0.5)
plt.legend()
plt.show()
