import pickle
from pathlib import Path

import pandas as pd

from backtest import BacktestConfig, run_backtest
from metrics import summarize_all
from strategies import Constraints, default_strategies
from universe import ASSET_CLASS, BOND_TICKERS, EQUITY_TICKERS, TICKERS

DATA_DIR = Path('data')
RESULTS_DIR = Path('results')
RESULTS_DIR.mkdir(exist_ok=True)

returns = pd.read_csv(DATA_DIR / 'returns.csv', index_col=0, parse_dates=True)
returns = returns[TICKERS]
constraints = Constraints(sector_map=ASSET_CLASS, sector_cap=0.40, max_weight=0.25)
long_only = Constraints()
config = BacktestConfig()

main_results = []
long_only_results = []
for strategy in default_strategies(EQUITY_TICKERS, BOND_TICKERS):
    main_results.append(run_backtest(returns, strategy, constraints, config))
    long_only_results.append(run_backtest(returns, strategy, long_only, config))

main_summary = summarize_all(main_results)
long_only_summary = summarize_all(long_only_results)

cost_results = {10: main_summary}
for cost_bps in [0, 25]:
    config = BacktestConfig(cost_bps=cost_bps)
    results = []
    for strategy in default_strategies(EQUITY_TICKERS, BOND_TICKERS):
        results.append(run_backtest(returns, strategy, constraints, config))
    cost_results[cost_bps] = summarize_all(results)

with open(RESULTS_DIR / 'main_results.pkl', 'wb') as file:
    pickle.dump(main_results, file)
with open(RESULTS_DIR / 'long_only_results.pkl', 'wb') as file:
    pickle.dump(long_only_results, file)
with open(RESULTS_DIR / 'cost_sensitivity.pkl', 'wb') as file:
    pickle.dump(cost_results, file)

main_summary.to_csv(RESULTS_DIR / 'main_summary.csv')
long_only_summary.to_csv(RESULTS_DIR / 'long_only_summary.csv')
pd.concat(cost_results, names=['cost_bps', 'strategy']).to_csv(
    RESULTS_DIR / 'cost_sensitivity.csv'
)
