import numpy as np
import pandas as pd

from strategies import check_weights


class BacktestConfig:
    def __init__(self, estimation_window_days=504, rebalance_freq='ME', cost_bps=10.0, starting_capital=1.0):
        self.estimation_window_days = estimation_window_days
        self.rebalance_freq = rebalance_freq
        self.cost_bps = cost_bps
        self.starting_capital = starting_capital


def run_backtest(returns, strategy, constraints, config):
    dates = returns.index
    date_series = pd.Series(dates, index=dates)
    rebal_dates = date_series.resample(config.rebalance_freq).last().dropna()
    rebal_dates = pd.DatetimeIndex(rebal_dates.values)               # actual final trading day of each period
    rebal_dates = rebal_dates[rebal_dates < dates[-1]]               # no terminal trade without a holding period
    rebal_dates = rebal_dates[dates.get_indexer(rebal_dates) >= config.estimation_window_days - 1]

    first_day = dates.get_loc(rebal_dates[0])
    gross_returns = pd.Series(0.0, index=dates[first_day:])
    net_returns = pd.Series(0.0, index=dates[first_day:])
    weights_log = {}
    turnover_log = {}
    current_weights = np.zeros(returns.shape[1])
    cost_per_unit = config.cost_bps / 10000
    tickers = list(returns.columns)

    for day in range(first_day, len(dates)):
        date = dates[day]
        daily_returns = returns.iloc[day].values
        gross_return = float(current_weights @ daily_returns)
        current_weights = current_weights * (1 + daily_returns) / (1 + gross_return)
        cost = 0.0

        if date in rebal_dates:
            start_day = day + 1 - config.estimation_window_days
            window = returns.iloc[start_day:day + 1]               # fit at the close, hold from the next day
            target_weights = strategy.allocate(window, constraints)
            check_weights(target_weights, tickers, constraints)
            turnover = np.abs(target_weights - current_weights).sum()
            cost = turnover * cost_per_unit
            current_weights = target_weights.copy()
            weights_log[date] = target_weights.copy()
            turnover_log[date] = turnover

        gross_returns.loc[date] = gross_return
        net_returns.loc[date] = (1 + gross_return) * (1 - cost) - 1

    equity = config.starting_capital * (1 + net_returns).cumprod()
    equity.loc[dates[first_day - 1]] = config.starting_capital       # include the value before initial entry cost
    equity = equity.sort_index()
    return {
        'equity': equity,
        'weights': pd.DataFrame.from_dict(weights_log, orient='index', columns=tickers),
        'turnover': pd.Series(turnover_log),
        'gross_returns': gross_returns,
        'net_returns': net_returns,
        'strategy': strategy.name,
    }
