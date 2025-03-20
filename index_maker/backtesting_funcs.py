import pandas as pd
import warnings
from .util_funcs import date_parser, transpose_weights
from typing import Tuple, Dict, List, Union


def make_hyp_shares(prices: pd.DataFrame, 
                    date: pd.Timestamp, 
                    weights: Dict[str, float], 
                    market_cap: float) -> Dict[str, float]:
    """
    Calculates hypothetical shares for each stock based on (initial) market cap and target weights.
    """

    companies = prices.columns.tolist() 
    all_hyp_shares_dict = {key: 0 for key in companies}
    hyp_shares = {}
    for stock in prices.columns:
        price = prices.loc[date, stock]
        weight = weights.get(stock, 0)
        if price > 0 and weight > 0:
            hyp_shares[stock] = (market_cap * weight) / price

    all_hyp_shares_dict.update(hyp_shares)
    return all_hyp_shares_dict


def calc_mark_cap(prices: pd.DataFrame, 
                  date: pd.Timestamp, 
                  hyp_shares: Dict[str, float]) -> float:
    """
    Calculates the market capitalization based on hypothetical shares and stock prices.
    """
    prices = prices.fillna(0)
    return sum(
        hyp_shares.get(stock, 0) * prices.loc[date, stock]
        for stock in prices.columns if stock in hyp_shares)


def set_index_dates(price_dates: pd.DatetimeIndex, 
                    rebal_dates: List[pd.Timestamp],
                    first_date: Union[str, pd.Timestamp, None] = None
                    ) -> Tuple[pd.Timestamp, pd.DatetimeIndex, pd.Timestamp, pd.DatetimeIndex]:
    """
    Ensures the correct input for the first index date and returns:
    - first index date (if provided)
    - last rebalance date
    - all the dates from the last rebalance date onwards (Gross Index dates)
    """

    if first_date is not None:
        first_date = date_parser(first_date)

    if first_date < price_dates[0]:
        first_date = price_dates[0]
        #raise ValueError("The first index date is older than the first date in the price dataset")

    if first_date not in price_dates:
        not_available_date = first_date
        first_date = price_dates[price_dates < first_date].max()
        warnings.warn(f"""
            There is no price data corresponding to the first date {not_available_date}.
            Using the first previous available date {first_date} as the index start date.
        """, UserWarning)

    if min(rebal_dates) <= first_date <= max(rebal_dates):
        last_rebal_date = max(date for date in rebal_dates if date <= first_date)
    else:
        last_rebal_date = first_date  # Default to `first_date` if no rebalance date is found

    # Find the index locations for slicing
    last_rebal_date_loc = price_dates.get_loc(last_rebal_date)

    return (
        first_date,
        last_rebal_date,
        price_dates[last_rebal_date_loc:]
    )



def set_inital_weights(first_date: pd.Timestamp, 
                       weights: pd.DataFrame) -> pd.Series:
    """
    Sets initial weights for the index based on the first available date or assigns equal weights if not available.
    """

    if weights.index.min() <= first_date <= weights.index.max():
        last_rebal_date = weights.index[weights.index <= first_date].max()
        initial_weights = weights.loc[last_rebal_date]
    else:
        raise ValueError("The first date is not within the range of the available weights dataset")

    return initial_weights



def make_index_backtest(index_start_level: float,
               initial_divisor: float,
               weights: pd.DataFrame,
               prices: pd.DataFrame,
               rebalance_dates: List[pd.Timestamp],
               first_index_date: Union[str, pd.Timestamp, None] = None
               ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.DataFrame]:
    """
    Constructs an index by calculating index levels, weights, and shares based on rebalancing dates and market prices.
    """

    divisor = initial_divisor
    initial_market_cap = index_start_level * divisor 

    index_levels = []
    daily_shares_list = []
    daily_total_market_value_list = []

    first_index_date, last_rebalancing_date, gross_index_dates  =  set_index_dates(prices.index, rebalance_dates, first_index_date )
    initial_weights  =                                             set_inital_weights(first_index_date, weights)
    hypothetical_shares =                                          make_hyp_shares(prices, last_rebalancing_date, initial_weights, initial_market_cap)


    shares_data = pd.DataFrame(index = gross_index_dates, columns=prices.columns).astype(float) # placehoder df for shares
    prices = prices[prices.index >= last_rebalancing_date]  # this allows for setting the custom index start date
    
    for date in gross_index_dates:  # Iterate over each day in the historical data

        if date in rebalance_dates:  # Rebalance if it's a rebalancing date
            print(f"Rebalancing on {date}")
            current_weights = weights.loc[date]

            if not current_weights.empty:
                total_market_value = calc_mark_cap(prices, date, hypothetical_shares)
     
                hypothetical_shares = make_hyp_shares(prices, date, current_weights, total_market_value)
            else:
                print(f"No weights found for date {date}")


        # Update index level based on total market value and divisor
        total_market_value = calc_mark_cap(prices, date, hypothetical_shares)

        if total_market_value > 0:
            index_level = total_market_value / divisor
            index_levels.append(index_level)


        # save the hypothetical shares and total market value for the day
        shares_daily = hypothetical_shares.copy()
        shares_daily['index'] = date

        daily_shares_list.append(shares_daily)
        daily_total_market_value_list.append(total_market_value)
        
    # Create dataframes for shares, weights, and index level
    index_series = pd.Series(index_levels, index = gross_index_dates, name="Index Level")

    if first_index_date is not None:
        filtered = index_series.loc[first_index_date:]
        index_series = index_start_level * (filtered / filtered.iloc[0])

    shares_data.update(pd.DataFrame(daily_shares_list).set_index("index"))
    weights_data = (shares_data * prices).div(daily_total_market_value_list, axis=0)    
    weights_data_last_day = transpose_weights(weights_data)
    
    index_series = index_series[index_series.index.is_month_start]
   
    return shares_data, weights_data, weights_data_last_day, index_series, prices