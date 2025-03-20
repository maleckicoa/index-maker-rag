import pandas as pd


def make_df(stock_info_final, tickers):

    if not tickers:
        return pd.DataFrame()
    
    stock_info_columns = ['symbol', 'name', 'country', 'country_full_name', 'currency', 'stock_exchange',
                          'sector','industry', 'beta', 'return_coeff', 'volatility_coeff','market_cap_euro', 'avg_trade_vol_euro', 
                          'return','volatility', 'market_capitalization', 'average_trading_volume', 
                          'description']
    
    new_column_names = ['Symbol', 'Name', 'Country', 'Country Full Name', 'Currency', 'Stock Exchange',
                        'Sector', 'Industry', 'Beta', 'Annual Return', 'Annual Volatility', 'Market Cap. (€)', 'Avg. Trading Vol. (€)',
                        'Return Category', 'Volatility Category', 'Market Cap. Category', 'Avg. Trading Vol. Category',
                        'Description']

    # Filter stock_info_final to only include relevant columns
    stock_info_df = stock_info_final[stock_info_columns].copy()
    symbol_list = tickers.copy()

    # Filter rows where 'symbol' is in the tickers list
    filtered_df = stock_info_df[stock_info_df['symbol'].isin(symbol_list)]

    # Create a copy and rename columns
    df = filtered_df.copy()
    df.columns = new_column_names

    # Format specific columns
    df['Annual Return'] = (df['Annual Return'] * 100).round(2).astype(str) + ' %'
    df['Annual Volatility'] = (df['Annual Volatility'] * 100).round(2).astype(str) + '%'
    df['Market Cap. (€)'] = pd.to_numeric(df['Market Cap. (€)'], errors='coerce').round(0)
    df['Avg. Trading Vol. (€)'] = pd.to_numeric(df['Avg. Trading Vol. (€)'], errors='coerce').round(0)

    # Ensure symbols follow the exact order in symbol_list
    print("SYMBOL LIST", symbol_list)
    df['Symbol'] = pd.Categorical(df['Symbol'], categories=symbol_list, ordered=True)

    # Sort rows by the order defined in symbol_list
    df = df.sort_values("Symbol").reset_index(drop=True)
    
    # Add a "#" column for row numbering
    df.insert(0, "#", range(1, len(df) + 1))

    return df
