import pandas as pd
from typing import List, Union

def subset_market_cap(tickers: List[str], 
                      weighting_date: pd.Timestamp, 
                      market_caps: List[float], 
                      threshold: float) -> Union[pd.DataFrame, None]:
    """
    Creates a daily subset of the market cap DataFrame, filtering out companies below the threshold
    and calculating weights based on MarketCap.
    """
    df = pd.DataFrame({'FE Ticker': tickers, 'MarketCap': market_caps})
    df['MarketCap'] = pd.to_numeric(df['MarketCap'], errors='coerce')
    df = df[df['MarketCap'].notna() & (df['MarketCap'] > threshold)]

    if df.empty:
        print(f"Skipping date {weighting_date} due to no valid companies after filtering.")
        return None
    
    total_market_cap = df['MarketCap'].sum()
    df['Weighting'] = df['MarketCap'] / total_market_cap
    return df


def apply_reweighting(df: pd.DataFrame, 
                      max_cap: float, 
                      min_cap: float, 
                      max_iterations: int = 100) -> pd.DataFrame:
    """
    Applies capping and flooring to weights in the subset DataFrame, adjusting iteratively within max iterations.
    """
    iteration = 0
    while df['Weighting'].max() > max_cap and iteration < max_iterations:
        df['Weighting'] = df['Weighting'].apply(lambda x: min(x, max_cap))
        excess_weight = 1 - df['Weighting'].sum()
        free_weighting_indices = df[df['Weighting'] < max_cap].index
        free_weight_total = df.loc[free_weighting_indices, 'Weighting'].sum()
        if free_weight_total > 0:
            df.loc[free_weighting_indices, 'Weighting'] += (
                df.loc[free_weighting_indices, 'Weighting'] / free_weight_total
            ) * excess_weight
        iteration += 1

    while (df['Weighting'] < min_cap).any():
        below_min_cap_indices = df[df['Weighting'] < min_cap].index
        min_cap_shortfall = (min_cap - df.loc[below_min_cap_indices, 'Weighting']).sum()
        df.loc[below_min_cap_indices, 'Weighting'] = min_cap
        free_weighting_indices = df[
            (df['Weighting'] < max_cap) & (~df.index.isin(below_min_cap_indices))
        ].index
        free_weight_total = df.loc[free_weighting_indices, 'Weighting'].sum()
        if free_weight_total > 0:
            df.loc[free_weighting_indices, 'Weighting'] -= (
                df.loc[free_weighting_indices, 'Weighting'] / free_weight_total
            ) * min_cap_shortfall

    df['Weighting'] /= df['Weighting'].sum()
    return df


def generate_final_df(adjusted_date: pd.Timestamp, 
                      df_market_cap: pd.DataFrame, 
                      tickers: List[str]) -> pd.DataFrame:
    """
    Generates a final reweighted DataFrame row with weights, adding zeroes for missing stocks.
    """
    weights_with_zeros = {ticker: 0 for ticker in tickers}
    weights_with_zeros.update(dict(zip(df_market_cap['FE Ticker'], df_market_cap['Weighting'])))
    return pd.DataFrame([[adjusted_date] + list(weights_with_zeros.values())],
                        columns=['Rebalance Date'] + tickers)


def reweighting_process(row: pd.Series, 
                        tickers: List[str], 
                        mcap_threshold: float, 
                        max_cap_value: float, 
                        min_cap_value: float) -> pd.DataFrame:
    """
    Performs the rebalancing process for each row in the market cap DataFrame.
    """
    reweighting_date = row['Date']
    adjusted_date = row['Adjustment Date']
    market_caps = row[tickers].tolist()
    
    df_market_cap = subset_market_cap(tickers, reweighting_date, market_caps, mcap_threshold)
    if df_market_cap is None:
        return pd.DataFrame()  # Return empty DataFrame if no valid companies remain
    
    df_market_cap = apply_reweighting(df_market_cap, max_cap_value, min_cap_value)
    return generate_final_df(adjusted_date, df_market_cap, tickers)


def calculate_weights(df: pd.DataFrame, 
                      adjustment_dates_list: List[pd.Timestamp], 
                      macap_threshold: float, 
                      max_cap_value: float, 
                      min_cap_value: float, 
                      tickers: List[str]) -> pd.DataFrame:
    """
    Calculates weights for rebalancing, applying the process row-by-row and handling missing values.
    """

    df = df.copy()
    df['Adjustment Date'] = adjustment_dates_list

    results = df.apply(
        reweighting_process,
        axis=1,
        args=(tickers, macap_threshold, max_cap_value, min_cap_value)
    ).dropna()

    if results.empty:
        print("Warning: No rebalancing data found. Please verify input criteria and data.")
        result_min_last_df = pd.DataFrame(columns=['Rebalance Date'] + tickers)
    else:
        result_min_last_df = pd.concat(results.tolist(), ignore_index=True)
        result_min_last_df = result_min_last_df[['Rebalance Date'] + tickers]

    return result_min_last_df
