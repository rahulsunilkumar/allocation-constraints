import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252


def annualized_return(returns):
    growth = (1 + returns).prod()
    return growth ** (TRADING_DAYS_PER_YEAR / len(returns)) - 1


def annualized_vol(returns):
    return returns.std(ddof=1) * np.sqrt(TRADING_DAYS_PER_YEAR)


def sharpe_ratio(returns):
    vol = annualized_vol(returns)
    if vol == 0:
        return np.nan
    return returns.mean() * TRADING_DAYS_PER_YEAR / vol             # zero risk-free rate


def max_drawdown(equity):
    drawdown = equity / equity.cummax() - 1
    return -drawdown.min()


def calmar_ratio(returns, equity):
    drawdown = max_drawdown(equity)
    if drawdown == 0:
        return np.nan
    return annualized_return(returns) / drawdown


def sortino_ratio(returns, target=0):
    excess_returns = returns - target                              # target is a daily return
    shortfalls = np.minimum(excess_returns, 0)
    downside_vol = np.sqrt(np.mean(shortfalls ** 2) * TRADING_DAYS_PER_YEAR)
    if downside_vol == 0:
        return np.nan
    return excess_returns.mean() * TRADING_DAYS_PER_YEAR / downside_vol


def summarize_backtest(result):
    gross = result['gross_returns']
    net = result['net_returns']
    equity = result['equity']
    turnover = result['turnover']
    return {
        'strategy': result['strategy'],
        'ann_return_gross': annualized_return(gross),
        'ann_return_net': annualized_return(net),
        'ann_vol': annualized_vol(net),
        'sharpe_gross': sharpe_ratio(gross),
        'sharpe_net': sharpe_ratio(net),
        'sortino': sortino_ratio(net),
        'max_drawdown': max_drawdown(equity),
        'calmar': calmar_ratio(net, equity),
        'avg_turnover': turnover.mean(),
        'total_cost_drag': annualized_return(gross) - annualized_return(net),
        'n_rebalances': len(turnover),
    }


def summarize_all(results):
    rows = [summarize_backtest(result) for result in results]
    return pd.DataFrame(rows).set_index('strategy')
