# Allocation Constraints for ETF Portfolios

When do allocation constraints help? This project compares equal weight, 60/40, minimum variance, maximum Sharpe, and risk parity across 18 ETFs. Using daily data from 2007–2024, I evaluate monthly allocations from 2009 onward and look at how allocation caps and trading costs change growth, risk, and performance.

## Findings

- With allocation caps and a trading cost of 10 basis points per dollar traded, minimum variance has the highest Sharpe, 0.925, while the capped equal-weight baseline has the highest annualized growth, 9.13%.
- Caps improve minimum variance's Sharpe while increasing its volatility. They reduce its heavy bond allocation, changing both its growth and risk rather than simply making it safer.
- Maximum Sharpe trades about eight times as much as 60/40 and has a lower realized Sharpe even before costs. Caps help some strategies and hurt others in this sample.

[Read the paper](https://github.com/rahulsunilkumar/allocation-constraints/blob/main/writeup/writeup.pdf) for the mathematics, results, and limitations.
