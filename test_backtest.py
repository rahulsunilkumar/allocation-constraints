import unittest

import numpy as np
import pandas as pd

from backtest import BacktestConfig, run_backtest
from metrics import sharpe_ratio, sortino_ratio
from strategies import Constraints, RiskParity, check_weights, default_strategies
from universe import ASSET_CLASS, BOND_TICKERS, EQUITY_TICKERS, TICKERS


class PortfolioChecks(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(42)
        dates = pd.bdate_range('2019-01-01', periods=800)
        vol = np.linspace(0.005, 0.02, len(TICKERS))
        data = rng.normal(0.0003, vol, (len(dates), len(TICKERS)))
        self.returns = pd.DataFrame(data, index=dates, columns=TICKERS)
        self.constraints = Constraints(ASSET_CLASS, sector_cap=0.4, max_weight=0.25)

    def test_all_strategies_respect_caps(self):
        for strategy in default_strategies(EQUITY_TICKERS, BOND_TICKERS):
            with self.subTest(strategy=strategy.name):
                weights = strategy.allocate(self.returns.iloc[:504], self.constraints)
                check_weights(weights, TICKERS, self.constraints)
                if strategy.name == '60/40':
                    bond_indices = [TICKERS.index(ticker) for ticker in BOND_TICKERS]
                    self.assertAlmostEqual(weights[bond_indices].sum(), 0.4, places=6)

    def test_risk_parity_diagonal_covariance(self):
        rng = np.random.default_rng(1)
        data = rng.normal(size=(200, 3))
        data = data - data.mean(axis=0)
        orthogonal, _ = np.linalg.qr(data)
        vols = np.array([0.01, 0.02, 0.04])
        returns = pd.DataFrame(orthogonal * vols)
        weights = RiskParity().allocate(returns, Constraints())
        expected = (1 / vols) / (1 / vols).sum()
        np.testing.assert_allclose(weights, expected, atol=1e-5)

    def test_calendar_drift_and_cost_accounting(self):
        class FixedAllocation:
            name = 'fixed'

            def allocate(self, returns_window, constraints):
                return np.array([0.5, 0.5])

        dates = pd.bdate_range('2021-01-01', '2021-05-10')
        returns = pd.DataFrame({'a': 0.01, 'b': 0.0}, index=dates)
        config = BacktestConfig(estimation_window_days=5, cost_bps=10)
        result = run_backtest(returns, FixedAllocation(), Constraints(), config)
        expected_dates = pd.to_datetime(['2021-01-29', '2021-02-26', '2021-03-31', '2021-04-30'])
        pd.testing.assert_index_equal(result['weights'].index, expected_dates)
        self.assertAlmostEqual(result['net_returns'].iloc[0], -0.001)
        self.assertAlmostEqual(result['gross_returns'].iloc[1], 0.005)
        drifted_weight = 0.5 * 1.01 / 1.005
        self.assertAlmostEqual(result['gross_returns'].iloc[2], drifted_weight * 0.01)
        date = pd.Timestamp('2021-02-26')
        gross = result['gross_returns'].loc[date]
        cost = result['turnover'].loc[date] * 0.001
        self.assertAlmostEqual(result['net_returns'].loc[date], (1 + gross) * (1 - cost) - 1)
        reconstructed = (1 + result['net_returns']).cumprod()
        np.testing.assert_allclose(result['equity'].loc[reconstructed.index], reconstructed)

    def test_future_returns_do_not_change_earlier_allocations(self):
        strategy = RiskParity()
        config = BacktestConfig(estimation_window_days=60)
        first = run_backtest(self.returns, strategy, self.constraints, config)
        changed = self.returns.copy()
        changed.iloc[500:] = changed.iloc[500:] * 2
        second = run_backtest(changed, strategy, self.constraints, config)
        cutoff = self.returns.index[499]
        pd.testing.assert_frame_equal(first['weights'].loc[:cutoff], second['weights'].loc[:cutoff])

    def test_metric_definitions(self):
        returns = pd.Series([0.01, -0.02, 0.03, 0.0])
        expected_sharpe = returns.mean() / returns.std(ddof=1) * np.sqrt(252)
        expected_sortino = returns.mean() * 252 / np.sqrt(0.02 ** 2 / 4 * 252)
        self.assertAlmostEqual(sharpe_ratio(returns), expected_sharpe)
        self.assertAlmostEqual(sortino_ratio(returns), expected_sortino)

    def test_infeasible_caps_raise(self):
        with self.assertRaises(RuntimeError):
            RiskParity().allocate(self.returns.iloc[:504], Constraints(max_weight=0.01))


if __name__ == '__main__':
    unittest.main()
