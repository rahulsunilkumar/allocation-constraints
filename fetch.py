from pathlib import Path

import yfinance as yf

from universe import TICKERS

DATA_DIR = Path('data')
DATA_DIR.mkdir(exist_ok=True)

raw = yf.download(TICKERS, start='2007-01-01', end='2024-12-31', auto_adjust=True, progress=False)
prices = raw['Close'].reindex(columns=TICKERS).dropna(how='all')
prices = prices.loc[prices.dropna().index[0]:]
returns = prices.pct_change(fill_method=None).iloc[1:]

prices.to_csv(DATA_DIR / 'prices.csv')
returns.to_csv(DATA_DIR / 'returns.csv')
