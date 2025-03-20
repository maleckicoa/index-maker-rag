import pandas as pd
pd.set_option('display.max_rows', None)
import pickle
import os
import logging
from dotenv import set_key, load_dotenv

import matplotlib
matplotlib.use("Agg") 
import matplotlib.pyplot as plt

from datetime import datetime, timedelta
from typing import Tuple, List, Union, Optional
from pytz import timezone
from dotenv import load_dotenv

from .util_funcs import * 
from .price_funcs import *
from .reweight_funcs import *
from .backtesting_funcs import *


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
price_file_path = os.path.join(parent_dir, 'files', 'prices_trimmed.pkl')
mcaps_file_path = os.path.join(parent_dir, 'files', 'mcaps_trimmed.pkl')
env_file_path = os.path.join(parent_dir, '.env')
#logger.info(f"Script directores: {env_file_path}")



def make_index_tool(ticker_input: Optional[str] = None, _input=None,) -> str:
    
    if ticker_input != "default" and ticker_input != "" and ticker_input is not None: 
        logger.info(f"MAKE INDEX TOOL - TICKERS RECEIVED AS ARGUMENT: {ticker_input}")
        ticker_list = [ticker.strip().upper() for ticker in ticker_input.split(",")]

    else:
        logger.info(f"MAKE INDEX TOOL - NO TICKERS RECEIVED AS ARGUMENT")
        load_dotenv(dotenv_path=env_file_path, override=True)
        ticker_str = os.getenv("TICKERS", "")
        if ticker_str:
            ticker_list = ticker_str.split(",") if ticker_str else []
            logger.info(f"MAKE INDEX TOOL - FORWARDING EXISTING .ENV TICKERS {ticker_list}")

    return make_index(ticker_list)


def make_index(ticker_list): 
   
    with open(price_file_path, 'rb') as file:
        prices_trimmed = pickle.load(file)

    with open(mcaps_file_path, 'rb') as file:
        mcaps_trimmed = pickle.load(file)

    all_ticker_list = list(prices_trimmed.columns)
    removed_tickers = [item for item in ticker_list if item not in all_ticker_list]
    ticker_list = [item for item in ticker_list if item in all_ticker_list]

    if removed_tickers:
        logger.info(f"MAKE INDEX - TICKERS NOT FOUND: {removed_tickers}")
    
    prices_trimmed.rename(columns={'date': 'Date'}, inplace=True)
    mcaps_trimmed.rename(columns={'date': 'Date'}, inplace=True)

    from .inputs import (
        file_path, mcap_threshold, max_cap_value, min_cap_value, scenario,
        date_adjustment_days, first_index_date, index_start_level,
        initial_divisor, index_type_list, save_results,
        ignore_past_dividends, parent_dir
    )

    ticker_list.insert(0, 'Date')

    prices_selected = prices_trimmed.copy()
    mcaps_selected = mcaps_trimmed.copy()

    adj_prices_df = prices_selected[ticker_list]
    mcap_df= mcaps_selected[ticker_list]

    for index_type in index_type_list:
        logger.info(f"MAKE INDEX - FUNCTION INPUT {ticker_list}")
        
        #mcap_df, prices_df, divs_df, country_df, tax_df = read_mcap_and_prices(file_path)
        #adj_prices_df = adjust_prices(prices_df, divs_df, country_df, tax_df, ignore_past_dividends, first_index_date, index_type = index_type)
        
        mcap_filter_df = filter_mcap(scenario=scenario, weekday = 4, df=mcap_df)
        selection_dates_list, rebalance_dates_list = get_rebalance_dates(mcap_filter_df, adj_prices_df, offset_days = date_adjustment_days)
        mcap_filter_df = mcap_filter_df[mcap_filter_df['Date'].isin(selection_dates_list)] # Market cap only includes the reweighting dates
        
        tickers = mcap_df.columns[1:].tolist() # get the list of all companies, before filtering
        mcap_weights_df = calculate_weights(mcap_filter_df, rebalance_dates_list, mcap_threshold, max_cap_value, min_cap_value, tickers)
        weights, prices, rebalance_dates =  prepare_for_index(mcap_weights_df, adj_prices_df)

        shares_data, weights_data, weights_data_last_day, index_series, prices_data = make_index_backtest(index_start_level = index_start_level, 
                                                                initial_divisor = initial_divisor, 
                                                                weights = weights, 
                                                                prices = prices, 
                                                                rebalance_dates = rebalance_dates,
                                                                first_index_date = first_index_date)
        

        if "Date" in ticker_list:
            ticker_list.remove("Date")
        ticker_str = ",".join(ticker_list)
        set_key(env_file_path, "TICKERS", ticker_str)
        logger.info(f"MAKE INDEX - QUERY TICKERS SAVED TO GLOBAL ENV: {ticker_str}")
        #plot_index(series = index_series, index_type = index_type)

        if len(ticker_list)>0:
            text_avalable_tickers = f"Please find below the historical index performance for following tickers: {', '.join(ticker_list)}"
        else:
            text_removed_tickers = ""

        if len(removed_tickers)>0:
            text_removed_tickers = f"Following tickers in your request were not found: {', '.join(removed_tickers)}"
        else:
            text_removed_tickers = ""


        return  index_series.to_dict(), text_avalable_tickers, text_removed_tickers
