# Allocation Constraints

This project studies how portfolio allocation rules, allocation caps, and transaction costs affect historical performance.

It compares equal weight, 60/40, minimum variance, maximum Sharpe, and risk parity portfolios across 18 ETFs.

## Experiment

- Data covers January 2007 through December 2024.
- Portfolios are long only, fully invested, and rebalanced monthly.
- The main experiment caps each ETF at 25% and each asset class at 40% at rebalance.
- Weights can drift between rebalances, so caps apply to target weights rather than daily weights.
- Risk estimates use a trailing window of 504 trading days.
- Transaction costs are tested at 0, 10, and 25 basis points per dollar traded.
- The uncapped comparison removes allocation caps but still prohibits short selling.

## Project Structure

- `universe.py`: ETF list and asset-class mapping
- `strategies.py`: portfolio objectives and optimization
- `backtest.py`: rebalancing, returns, and costs
- `metrics.py`: performance calculations
- `fetch.py`: price and return data
- `run_analysis.py`: portfolio comparison and cost analysis
- `make_plots.py`: charts and paper figures

## Results

Data, results, and figures are stored in the `data/`, `results/`, and `figures/` folders.

The research paper is available in `writeup/writeup.pdf`.
