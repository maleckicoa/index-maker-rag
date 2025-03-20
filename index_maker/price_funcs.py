import pandas as pd
import numpy as np
from .inputs import first_index_date, ignore_past_dividends


def adjust_prices(prices_df: pd.DataFrame, 
                  dividends_df: pd.DataFrame, 
                  country_df: pd.DataFrame, 
                  tax_df: pd.DataFrame,
                  ignore_past_dividends:bool,
                  first_index_date: str | None,
                  index_type: str,
                  ) -> pd.DataFrame:
    
    '''
    Adjusts the prices dataframe based on Index Type (PR, GTR, NTR) and returns a new prices dataframe.
    '''
    
    if index_type not in ['PR', 'GTR', 'NTR']:
        raise ValueError('index_type must be one of PR, GTR, NTR')
    
    if index_type == 'PR':
        return prices_df
    
    dividend_prices_df = prices_df.iloc[:,1:].fillna(0).copy()
    divs_df = dividends_df.copy()

    raw_prices = prices_df.iloc[:, 1:].copy()
    raw_price_returns = (raw_prices/raw_prices.shift(1)) - 1  # Percentage change
    raw_price_returns = raw_price_returns.fillna(0)

    first_raw_prices = raw_prices.apply(lambda col: col.where(col.index == col.first_valid_index(), other=np.nan))
    first_raw_prices.fillna(0,inplace=True)

    if first_index_date is not None and ignore_past_dividends:
        print('Ignoring Dividends before Index Start Date')
        divs_df.loc[divs_df["Date"] < first_index_date, divs_df.columns != "Date"] = 0
    else:
        print('Dividends before the Index Start Date are included in the calculations')

    if index_type == 'GTR':
        final_divs_df = divs_df.copy()

    if index_type == 'NTR':
        country_df.rename(columns={'Input': 'Ticker', 'Country of Inc.': 'Country'}, inplace=True)  
        tax_df.rename(columns={'COUNTRY OF INCORP.': 'Country','WITHHOLDING TAX':'Tax' }, inplace=True)
        ticker_tax_map_df = pd.merge(country_df, tax_df, how='left', on='Country')
        ticker_tax_map_dict = dict(zip(ticker_tax_map_df['Ticker'], ticker_tax_map_df['Tax']))

        tax_adj_divs_df = divs_df.copy()
        for ticker in ticker_tax_map_dict:
            if ticker in tax_adj_divs_df.columns:
                tax_adj_divs_df[ticker] = tax_adj_divs_df[ticker] * (1 - ticker_tax_map_dict[ticker])
        final_divs_df = tax_adj_divs_df.copy()


    result_df = pd.DataFrame(index = dividend_prices_df.index, columns=dividend_prices_df.columns) # placeholder df
    previous_dividend_prices_row = pd.Series(0, index=dividend_prices_df.columns)                  # all zero series needed for first row

    for i, _ in dividend_prices_df.iterrows():
        dividend_prices_row = dividend_prices_df.loc[i]
        raw_price_returns_row = raw_price_returns.loc[i]
        dividends_row = final_divs_df.loc[i]
        first_raw_prices_row = first_raw_prices.loc[i]

        if i==0:
            calculated_values = dividends_row + dividend_prices_row + (dividend_prices_row * raw_price_returns_row)
        else:
            calculated_values = dividends_row + (previous_dividend_prices_row + first_raw_prices_row) + (previous_dividend_prices_row * raw_price_returns_row)

        result_df.loc[i] = calculated_values
        previous_dividend_prices_row = calculated_values
    
    result_df = result_df.astype(float)
    result_df = result_df.replace(0, np.nan)
    result_df.insert(0, 'Date', prices_df['Date'])
    return result_df