# Allocation constraints

This experiment compares equal weight, 60/40, minimum variance, maximum Sharpe,
and risk parity portfolios across 18 ETFs. It tests how allocation caps and
transaction costs change historical performance.

## Run

Run these commands from this folder:

```bash
venv/bin/python -m pip install -r requirements.txt
venv/bin/python -m unittest -v test_backtest
venv/bin/python fetch.py
venv/bin/python run_analysis.py
venv/bin/python make_plots.py
```

Prices and returns are saved in `data/`, results in `results/`, and figures in
`figures/`. Figures are saved as PNG and used directly in the LaTeX paper.
If Matplotlib cannot write its cache, prefix the plotting command with
`MPLCONFIGDIR=/tmp/allocation-matplotlib`.

The paper is in `writeup/writeup.tex`. Build it from the project directory with:

```bash
cd writeup
latexmk -pdf writeup.tex
```

Open `writeup/writeup.pdf` from the project directory to read the compiled paper.

## Reading order

1. `universe.py`: the asset list and asset-class mapping used by all scripts.
2. `strategies.py`: objectives, allocation caps, and numerical optimization.
3. `backtest.py`: rebalance dates, weight drift, returns, and costs.
4. `metrics.py`: performance calculations.
5. `fetch.py`: adjusted prices and daily returns.
6. `run_analysis.py`: main comparison and cost sensitivity.
7. `make_plots.py`: result loading and paper figures in one file.

## Experiment definitions

- Data request: January 2007 through December 2024. The download end date is
  exclusive. The scripts assume complete, finite returns, ordered unique dates,
  and sufficient history, including coverage for the 2020 chart.
- The trailing estimation window contains 504 trading days.
- Rebalancing occurs at the last available trading day of each month.
  Estimates use returns through that close; new weights earn returns starting
  on the next trading day. This assumes execution at the observed close and
  does not model execution delay or market impact.
- All strategies are long only and fully invested. The main experiment limits
  each ETF to 25% and each mapped asset class to 40% at rebalance. Weights drift
  between rebalances, so these are target-weight limits, not daily limits.
- The code retains the parameter name `sector_cap`, but the mapping describes
  broad asset classes, not underlying company sectors. Overlapping ETF
  holdings are not decomposed into their underlying exposures.
- Under caps, equal weight means the feasible weights closest to 1/n in
  squared distance. It is no longer literal equal weight. The 60/40 baseline
  preserves its 60% equity and 40% bond totals while adjusting within those
  sleeves to respect the caps. Real estate is included in its equity sleeve.
- Constrained risk parity minimizes deviations from equal risk shares. Caps
  can prevent an exact equal-risk solution.
- The comparison called `long_only` removes the allocation caps. It still
  prohibits short selling and requires weights to sum to one.
- Cost is 0, 10, or 25 basis points per dollar traded. Traded notional is
  `sum(abs(target_weights - drifted_weights))`, including purchases and sales.
  Initial entry is charged; terminal liquidation is not.
- Trading costs are deducted proportionally from wealth, then target weights
  apply to the remaining wealth. Turnover uses weights before costs; this is
  a proportional-cost approximation, not a cash-flow execution simulation.
- Gross and net returns cover identical dates. The first date records entry
  cost with zero gross return. Equity includes the preceding capital value
  so drawdown includes that initial loss.
- Sharpe uses mean daily return divided by sample daily volatility, annualized
  with 252 trading days and a zero risk-free rate. Sortino uses the root mean
  squared shortfall across all days, also with a zero default target.
- The crisis chart covers January–June 2020. With data beginning in 2007 and
  a two-year warm-up, this experiment cannot claim a full 2008 crisis test.

## Checks

The synthetic checks cover cap enforcement, infeasible allocations,
month-end scheduling, drift, cost reconciliation, risk parity on a diagonal
covariance matrix, metric definitions, and future-data isolation.

The paper uses the saved 2007–2024 data, with evaluation beginning on January
30, 2009 after the estimation warm-up. SLSQP is a local optimizer, and numerical
success does not prove a global optimum. The experiment does not include
significance tests or confidence intervals.
