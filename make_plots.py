import pickle
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

RESULTS_DIR = Path('results')
FIG_DIR = Path('figures')
FIG_DIR.mkdir(exist_ok=True)

plt.rcParams.update({
    'font.family': 'serif',
    'font.size': 10,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'savefig.bbox': 'tight',
    'savefig.dpi': 200,
})
COLORS = {
    'Equal Weight': 'tab:blue', '60/40': 'tab:orange',
    'Minimum Variance': 'tab:green', 'Maximum Sharpe': 'tab:red',
    'Risk Parity': 'tab:purple',
}


def save_figure(fig, name):
    fig.savefig(FIG_DIR / f'{name}.png')
    plt.close(fig)


with open(RESULTS_DIR / 'main_results.pkl', 'rb') as file:
    results = pickle.load(file)
summary = pd.read_csv(RESULTS_DIR / 'main_summary.csv', index_col=0)
long_only_summary = pd.read_csv(RESULTS_DIR / 'long_only_summary.csv', index_col=0)
cost_results = pd.read_csv(RESULTS_DIR / 'cost_sensitivity.csv')

fig, ax = plt.subplots(figsize=(7, 4))
for result in results:
    equity = result['equity']
    ax.plot(equity.index, equity, label=result['strategy'], color=COLORS[result['strategy']])
ax.set_yscale('log')
ax.set_ylabel('Portfolio value ($1 invested, log scale)')
ax.legend(frameon=False)
save_figure(fig, 'equity')

fig, ax = plt.subplots(figsize=(7, 4))
for result in results:
    equity = result['equity']
    drawdown = 100 * (equity / equity.cummax() - 1)
    ax.plot(drawdown.index, drawdown, label=result['strategy'], color=COLORS[result['strategy']])
ax.set_ylabel('Drawdown (%)')
ax.legend(frameon=False)
save_figure(fig, 'drawdowns')

fig, ax = plt.subplots(figsize=(6, 3))
sharpes = summary['sharpe_net'].sort_values()
ax.barh(sharpes.index, sharpes, color=[COLORS[name] for name in sharpes.index])
ax.axvline(0, color='black', linewidth=0.5)
ax.set_xlabel('Net Sharpe ratio (10 bps per dollar traded)')
save_figure(fig, 'sharpe')

fig, ax = plt.subplots(figsize=(7, 4))
positions = np.arange(len(summary))
ax.bar(positions - 0.2, long_only_summary.loc[summary.index, 'sharpe_net'], width=0.4, label='Long only', color='lightgray')
ax.bar(positions + 0.2, summary['sharpe_net'], width=0.4, label='Long only + allocation caps', color='tab:blue')
ax.set_xticks(positions, summary.index, rotation=20, ha='right')
ax.axhline(0, color='black', linewidth=0.5)
ax.set_ylabel('Net Sharpe ratio')
ax.legend(frameon=False, loc='lower center', bbox_to_anchor=(0.5, 1), ncol=2)
save_figure(fig, 'constraints')

fig, axes = plt.subplots(1, 2, figsize=(9, 4))
axes[0].barh(summary.index, summary['avg_turnover'] * 100, color='tab:blue')
axes[0].set_xlabel('Mean traded notional per rebalance (%)')
axes[1].barh(summary.index, summary['total_cost_drag'] * 10000, color='tab:orange')
axes[1].set_xlabel('Gross minus net CAGR (bps)')
fig.tight_layout()
save_figure(fig, 'turnover_and_cost')

fig, ax = plt.subplots(figsize=(6, 4))
for strategy in summary.index:
    values = cost_results[cost_results['strategy'] == strategy].sort_values('cost_bps')
    ax.plot(values['cost_bps'], values['sharpe_net'], marker='o', label=strategy, color=COLORS[strategy])
ax.set_xlabel('Cost (bps per dollar traded)')
ax.set_ylabel('Net Sharpe ratio')
ax.set_xticks([0, 10, 25])
ax.legend(frameon=False, loc='lower center', bbox_to_anchor=(0.5, 1), ncol=2)
save_figure(fig, 'cost_sensitivity')

fig, ax = plt.subplots(figsize=(7, 4))
for result in results:
    equity = result['equity']
    baseline = equity.loc[:'2019-12-31']
    period = equity.loc['2020-01-01':'2020-06-30']
    ax.plot(period.index, period / baseline.iloc[-1], label=result['strategy'], color=COLORS[result['strategy']])
ax.set_ylabel('Portfolio value (end of 2019 = 1)')
ax.legend(frameon=False)
fig.autofmt_xdate()
save_figure(fig, 'covid_2020')

for result in results:
    weights = result['weights']
    fig, ax = plt.subplots(figsize=(8, 5))
    image = ax.imshow(weights.T.values, aspect='auto', cmap='Blues', vmin=0, vmax=0.25)
    ax.set_yticks(range(len(weights.columns)), weights.columns)
    ticks = np.linspace(0, len(weights) - 1, 6, dtype=int)
    ax.set_xticks(ticks, weights.index[ticks].strftime('%Y-%m'), rotation=30, ha='right')
    ax.set_title(result['strategy'])
    fig.colorbar(image, ax=ax, label='Target weight at rebalance')
    name = result['strategy'].lower().replace(' ', '_').replace('/', '_')
    save_figure(fig, f'weights_{name}')
