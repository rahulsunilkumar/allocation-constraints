import numpy as np
from scipy.optimize import minimize

TRADING_DAYS_PER_YEAR = 252


class Constraints:
    def __init__(self, sector_map=None, sector_cap=None, max_weight=None, long_only=True):
        self.sector_map = {} if sector_map is None else sector_map
        self.sector_cap = sector_cap
        self.max_weight = max_weight
        self.long_only = long_only


def allocation_rules(tickers, constraints):
    rules = [{'type': 'eq', 'fun': lambda weights: weights.sum() - 1}]
    if constraints.sector_cap is not None:
        sectors = sorted(set(constraints.sector_map[ticker] for ticker in tickers))
        for sector in sectors:
            indices = []
            for index, ticker in enumerate(tickers):
                if constraints.sector_map[ticker] == sector:
                    indices.append(index)

            def sector_room(weights, indices=indices):              # keep this sector's indices
                return constraints.sector_cap - weights[indices].sum()

            rules.append({'type': 'ineq', 'fun': sector_room})
    return rules


def check_weights(weights, tickers, constraints):
    tolerance = 1e-6
    if not np.isfinite(weights).all() or abs(weights.sum() - 1) > tolerance:
        raise ValueError('allocation must be finite and sum to one')
    lower = 0 if constraints.long_only else -1
    upper = 1 if constraints.max_weight is None else constraints.max_weight
    if np.any(weights < lower - tolerance) or np.any(weights > upper + tolerance):
        raise ValueError('allocation violates position bounds')
    for rule in allocation_rules(tickers, constraints)[1:]:
        if rule['fun'](weights) < -tolerance:
            raise ValueError('allocation violates a sector cap')


def solve_allocation(objective, tickers, constraints, extra_rules=None, gradient=None):
    n_assets = len(tickers)
    starting_weights = np.ones(n_assets) / n_assets
    lower = 0 if constraints.long_only else -1
    upper = 1 if constraints.max_weight is None else constraints.max_weight
    rules = allocation_rules(tickers, constraints)
    if extra_rules is not None:
        rules.extend(extra_rules)

    result = minimize(
        objective,
        starting_weights,
        jac=gradient,
        method='SLSQP',
        bounds=[(lower, upper)] * n_assets,
        constraints=rules,
        options={'maxiter': 500, 'ftol': 1e-10},
    )
    if not result.success:                                         # never replace a failed fit silently
        raise RuntimeError(f'allocation failed: {result.message}')
    check_weights(result.x, tickers, constraints)
    for rule in rules:
        value = rule['fun'](result.x)
        if rule['type'] == 'eq' and abs(value) > 1e-6:
            raise ValueError('allocation violates a required total')
    return result.x


class EqualWeight:
    name = 'Equal Weight'

    def allocate(self, returns_window, constraints):
        tickers = list(returns_window.columns)
        target = np.ones(len(tickers)) / len(tickers)

        def objective(weights):                                   # closest feasible allocation to 1/n
            return np.sum((weights - target) ** 2)

        return solve_allocation(objective, tickers, constraints)


class SixtyForty:
    name = '60/40'

    def __init__(self, equity_tickers, bond_tickers):
        self.equity_tickers = equity_tickers
        self.bond_tickers = bond_tickers

    def allocate(self, returns_window, constraints):
        tickers = list(returns_window.columns)
        equity_indices = []
        bond_indices = []
        for index, ticker in enumerate(tickers):
            if ticker in self.equity_tickers:
                equity_indices.append(index)
            if ticker in self.bond_tickers:
                bond_indices.append(index)
        target = np.zeros(len(tickers))
        target[equity_indices] = 0.60 / len(equity_indices)
        target[bond_indices] = 0.40 / len(bond_indices)

        def objective(weights):                                   # keep the sleeves at 60/40
            return np.sum((weights - target) ** 2)

        sleeve_rules = [
            {'type': 'eq', 'fun': lambda weights: weights[equity_indices].sum() - 0.60},
            {'type': 'eq', 'fun': lambda weights: weights[bond_indices].sum() - 0.40},
        ]
        return solve_allocation(objective, tickers, constraints, sleeve_rules)


class MinimumVariance:
    name = 'Minimum Variance'

    def allocate(self, returns_window, constraints):
        cov = returns_window.cov().values * TRADING_DAYS_PER_YEAR

        def objective(weights):
            return weights @ cov @ weights

        def gradient(weights):
            return 2 * cov @ weights

        return solve_allocation(objective, list(returns_window.columns), constraints,
                                gradient=gradient)


class MaximumSharpe:
    name = 'Maximum Sharpe'

    def allocate(self, returns_window, constraints):
        mean_returns = returns_window.mean().values * TRADING_DAYS_PER_YEAR
        cov = returns_window.cov().values * TRADING_DAYS_PER_YEAR

        def objective(weights):
            portfolio_return = weights @ mean_returns
            portfolio_vol = np.sqrt(max(weights @ cov @ weights, 1e-12))
            return -portfolio_return / portfolio_vol

        return solve_allocation(objective, list(returns_window.columns), constraints)


class RiskParity:
    name = 'Risk Parity'

    def allocate(self, returns_window, constraints):
        cov = returns_window.cov().values * TRADING_DAYS_PER_YEAR
        n_assets = len(cov)

        def objective(weights):
            portfolio_var = max(weights @ cov @ weights, 1e-12)
            risk_shares = weights * (cov @ weights) / portfolio_var
            return np.sum((risk_shares - 1 / n_assets) ** 2)

        return solve_allocation(objective, list(returns_window.columns), constraints)


def default_strategies(equity_tickers, bond_tickers):
    return [EqualWeight(), SixtyForty(equity_tickers, bond_tickers),
            MinimumVariance(), MaximumSharpe(), RiskParity()]
