# Universal Portfolios

## Theory

A universal portfolio is an investment strategy that asymptotically performs as well as if the returns of the stock market were known. 
One can imagine that such an algorithm 'learns' the distribution of stock returns over time.
This name comes from the field of data compression where a universal compression scheme asymptotically performs as well as if the distribution of symbols was known.

In 1991, Thomas Cover introduced a universal portfolio that achieves this optimality by averaging over all possible portfolios, weighted by the current performance of each.
Let $b^U_{k+1}$ be the universal portfolio vector for the ($k+1$)th time period representing the proportion of wealth invested in each asset. 
Let $S_k(b)$ be the wealth of a portfolio after $k$ time periods where $b$ is any portfolio from the space of allowed ones, $B$.

$$ b^U_{k+1} = \frac{\int_B bS_k(b)db}{\int_B S_k(b)db} $$

In the long run, the growth rate of the universal portfolio approaches that of the best constant rebalanced portfolio in hindsight. 
Upon quantising the portfolio space, this is simply the portfolio that achieves the greatest wealth. 
We approximate $B$ using $N$ portfolios, $b^{(i)}$ with wealth $S^{(i)}$ for $i \in \{1, ..., N\}$, to arrive at a Monte Carlo approximation to this universal portfolio.

$$ \hat{b}^U_{k+1} = \frac{\sum_{i=1}^N b^{(i)}S^{(i)}_k}{\sum_{j=1}^N S^{(j)}_k} $$

To mirror realistic markets, we implement proportional transaction costs, $T$, on each rebalancing of the portfolio based on the amount of wealth displaced (bought or sold).
Say we hold the portfolio $b_k$ at time $k$ and the returns of the stocks drift this portfolio to $b_k'$.
If we have calculated the optimal portfolio for time period $k+1$ as $b_{k+1}$, then we must rebalance the portfolio from $b_k'$ to $b_{k+1}$.

$$ T = c\Vert b_k' - b_{k+1}\Vert _1 $$

## Program Description

The program implements and tests this universal portfolio algorithm using real data from Yahoo Finance.
The user selects the stocks and time period over which they wish to backtest.
The program outputs a plot of the variation of wealth over time using the universal portfolio, using the best constant rebalanced portfolio in hindsight and using the buy and hold strategies corresponding to each underlying stock.
Optionally, the user may add the effects of transaction costs and change the frequency at which the portfolios are rebalanced.

## Example Outputs

Some example plots are given using 2 underlying stocks of Ford Motor Company and Bank of America Corporation with no transaction costs and daily rebalancing.

<img width="900" height="400" alt="LogWealth_F-BAC" src="https://github.com/user-attachments/assets/a671617a-fe9a-4f6f-b2dc-8886ba55bd48" />
<img width="640" height="480" alt="Proportions_Ford-BAC" src="https://github.com/user-attachments/assets/17991924-9558-446f-aa99-69566c413583" />

