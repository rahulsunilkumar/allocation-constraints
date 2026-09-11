ASSET_CLASS = {
    'SPY': 'US Equity', 'QQQ': 'US Equity', 'IWM': 'US Equity', 'DIA': 'US Equity',
    'XLF': 'US Equity', 'XLE': 'US Equity', 'XLK': 'US Equity', 'XLV': 'US Equity',
    'XLU': 'US Equity', 'XLP': 'US Equity',
    'EFA': 'Intl Equity', 'EEM': 'Intl Equity', 'EWJ': 'Intl Equity',
    'TLT': 'Fixed Income', 'IEF': 'Fixed Income',
    'GLD': 'Commodity', 'USO': 'Commodity', 'VNQ': 'Real Estate',
}

TICKERS = list(ASSET_CLASS)
EQUITY_TICKERS = [ticker for ticker, asset_class in ASSET_CLASS.items()
                  if 'Equity' in asset_class or asset_class == 'Real Estate']
BOND_TICKERS = ['TLT', 'IEF']
