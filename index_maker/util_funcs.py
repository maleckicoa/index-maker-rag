import os
import pandas as pd 
from .inputs import scenarios, index_start_level, parent_dir
from datetime import timedelta
import matplotlib.pyplot as plt
from pytz import timezone
from datetime import datetime, timedelta
from typing import Tuple, List, Any

def read_mcap_and_prices(file_path: str, 
                         mcap_sheet: str = 'MarketCap', 
                         prices_sheet: str = 'Prices',
                         dividends_sheet: str = 'Dividends',
                         country_sheet: str = "Country of Incorp.",
                         tax_sheet: str = 'TAX'
                         ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Loads MarketCap and Prices data from an Excel file.
    """
    sheets_with_date = pd.read_excel(file_path, sheet_name=[mcap_sheet, prices_sheet, dividends_sheet], header=0, parse_dates=['Date'])
    mapping_sheets = pd.read_excel(file_path,  sheet_name=[country_sheet, tax_sheet], header=0)
    
    mcap_df = sheets_with_date[mcap_sheet]
    prices_df = sheets_with_date[prices_sheet]
    dividends_df = sheets_with_date[dividends_sheet]
    country_df = mapping_sheets[country_sheet]
    tax_df = mapping_sheets[tax_sheet]  


    dataframes = [mcap_df, prices_df, dividends_df]
    for df in dataframes:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.normalize()
        df.dropna(subset=['Date'], inplace=True)

    try:
        mcap_df.columns = prices_df.columns = dividends_df.columns
    except:
        raise ValueError(f"Columns in {mcap_sheet} and {prices_sheet} and {dividends_df} do not match")
    
    return mcap_df, prices_df, dividends_df, country_df, tax_df



def filter_mcap(scenario: str, 
                weekday: int, 
                df: pd.DataFrame, 
                scenarios: dict=scenarios) -> pd.DataFrame:
    """
    Filters the MarketCap DataFrame by scenario and weekday, returning rows for Nth Friday of specific months.
    """
    df = df.copy()
    df['Weekday'] = df['Date'].dt.weekday
    df['Month'] = df['Date'].dt.month
    df['Quarter'] = df['Date'].dt.to_period('Q')

    filter_friday_df = df[df['Weekday'] == weekday]

    params = scenarios[scenario]
    nth_friday = params['nth_friday']
    frequency = params['frequency']
    months = params.get('months', None)

    if frequency == 'Semi-Annual':
        filter_friday_months_df = filter_friday_df[filter_friday_df['Month'].isin(months)]
        filter_nth_friday_month_df = (
            filter_friday_months_df.groupby(filter_friday_months_df['Date'].dt.to_period('M'))
            .nth(nth_friday - 1)
            .reset_index(drop=True)
        )
    else:
        raise ValueError(f"Invalid frequency, check the Scenarios dictionary")
    
    return filter_nth_friday_month_df


def date_parser(date: Any) -> pd.Timestamp:
    if isinstance(date, pd.Timestamp):
        return date
    
    elif isinstance(date, str):
        try:
            date = pd.Timestamp(datetime.strptime(date, '%Y-%m-%d')).normalize()
        except ValueError:
            raise ValueError("The date must be a string in 'YYYY-MM-DD' format or a pandas Timestamp object.")
    else:
        raise ValueError("The date must be a string ('YYYY-MM-DD') or a pandas Timestamp object.")
    
    return date
    

def get_rebalance_dates(df_a: pd.DataFrame, 
                         df_b: pd.DataFrame, 
                         offset_days: int) -> Tuple[List[pd.Timestamp], List[pd.Timestamp]]:
    """
    Calculates adjustment dates based on a reweighting date and an offset in days.
    """
    list_a = pd.to_datetime(df_a.iloc[:, 0]).tolist()
    list_b = sorted(pd.to_datetime(df_b.iloc[:, 0]).tolist())  # Sort list_b for efficient searching

    reweighting_dates = []
    adjustment_dates = []

    for reweighting_date in list_a:
        target_date = reweighting_date + timedelta(days=offset_days)
        
        # Find the first date in list_b that is >= target_date
        adjustment_date = next((d for d in list_b if d >= target_date), None)

        if adjustment_date is None:
            print(f"Warning: Skipping the rebalancing date {reweighting_date}, because there is no available price data")
            continue
        
        reweighting_dates.append(reweighting_date.normalize())
        adjustment_dates.append(adjustment_date.normalize()) 
    
    return reweighting_dates, adjustment_dates


def prepare_for_index(weights_df: pd.DataFrame, 
                      prices_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DatetimeIndex]:
    
    """
    Prepares data for rebalancing by aligning weights df and prices df and setting the start date for price df.
    """

    if weights_df.empty:
        raise ValueError("weights_df is empty. No rebalancing data available.")

    # Align DataFrames and filter by the first rebalance date
    first_rebal_date = pd.to_datetime(weights_df['Rebalance Date']).min()
    prices_bkts_df = prices_df[prices_df['Date'] >= first_rebal_date].set_index('Date')
    weights_bkts_df = weights_df.set_index('Rebalance Date')

    # Normalize indices and extract rebalance dates
    weights_bkts_df.index = pd.to_datetime(weights_bkts_df.index).normalize()
    prices_bkts_df.index = pd.to_datetime(prices_bkts_df.index).normalize()
    rebal_dates = weights_bkts_df.index.intersection(prices_bkts_df.index).normalize()

    return weights_bkts_df.sort_index(), prices_bkts_df.sort_index(), rebal_dates


def transpose_weights(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes the weights on thre last day and transposes the dataframe 
    """
    weights_data_desc = df.sort_values(by=['Date'], ascending=False)
    column_list = list(df.columns)
    weights_list = weights_data_desc.iloc[0].tolist()
    weights_data_last_day = pd.DataFrame({
        'FactSet-ID/ISIN': column_list,
        'Shares/Weights': weights_list
        })
    return weights_data_last_day


def plot_index(series: pd.Series, index_type) -> None:
    """
    Plots an index level time series with labeled axes and a title.
    """
    plt.figure(figsize=(8, 5))
    plt.plot(series, label='Index Level')
    plt.xlabel('Date')
    plt.ylabel('Index Level')
    plt.title(f'Divisor Index Backtest (Starting at {index_start_level}), Index Type = {index_type}')
    plt.legend()
    plt.grid(True)
    plt.show()


def plot_multi_index(series: dict):
    
    if len(series)<=1:
        return
    
    plt.figure(figsize=(8, 5))
    for label, series in series.items():
        plt.plot(series, label=label)

    # Add legend, title, and labels
    plt.legend()
    plt.title("Multiple Index Backtest")
    plt.xlabel("Index")
    plt.ylabel("Values")
    plt.grid(True)
    plt.show()


def save_rebalancing_results(save_results: bool,
                             index_type: str,
                             mcap_weights_df: pd.DataFrame,
                             index_series: pd.Series,
                             market_cap_df: pd.DataFrame,
                             prices_df: pd.DataFrame,
                             adj_prices_df: pd.DataFrame,
                             mcap_filter_df: pd.DataFrame,
                             shares_data: pd.DataFrame,
                             weights_data: pd.DataFrame,
                             weights_data_last_day: pd.DataFrame) -> None:
    """
    Saves rebalancing results to an Excel file with the current CET timestamp, hiding specific sheets.
    """
    if not save_results:
        return

    if mcap_weights_df.empty:
        print("No results to export to Excel.")
        return

    # Calculate the first rebalance date and filter prices for backtesting
    first_rebalance_date = mcap_weights_df['Rebalance Date'].min()
    prices_backtesting_df = adj_prices_df[adj_prices_df['Date'] >= first_rebalance_date]

    # Get the current date and timestamp in CET
    cet = timezone('CET')
    current_timestamp_cet = datetime.now(cet).strftime('%Y%m%d_%H%M%S')
    current_date_cet = datetime.now(cet).strftime('%Y%m%d')
                                                  
    output_file_name_cet = os.path.join(parent_dir,f"NaroIX_Rebalancing_MinLast_{current_timestamp_cet}_{index_type}.xlsx")
    output_weights_file_name_cet =  os.path.join(parent_dir,f"Rebalancing_Weights_Upload_{index_type}_{current_date_cet}.csv")

    # Define data to save and sheets to hide
    data_to_save = {
        'Index Level': index_series,
        'MarketCap': market_cap_df,
        'Prices': prices_df,
        'Prices - Backtesting': prices_backtesting_df,
        'MCap - Selection Date': mcap_filter_df,
        'Weights - Rebalancing Date': mcap_weights_df,
        'Calculated Shares': shares_data,
        'Calculated Weights': weights_data,
    }
    sheets_to_hide = {'MarketCap', 'Prices', 'MCap - Selection Date', 'Calculated Shares', 'Calculated Weights'}

    # Save to Excel
    with pd.ExcelWriter(output_file_name_cet, engine='openpyxl', mode='w') as writer:
        for sheet_name, data in data_to_save.items():
            data.to_excel(writer, index = isinstance(data.index, pd.DatetimeIndex), sheet_name = sheet_name)
            if sheet_name in sheets_to_hide and sheet_name in writer.sheets:
                writer.sheets[sheet_name].sheet_state = 'hidden'

    weights_data_last_day.to_csv(output_weights_file_name_cet, index=False)

    print(f"Weights for rebalancing saved to {output_file_name_cet}")


def save_multi_index_df(save_results: bool,
                        dataframe: pd.DataFrame, 
                        sheet_name: str = "Index Levels") -> None:
        
        if not save_results:
            return

        cet = timezone('CET')
        current_timestamp_cet = datetime.now(cet).strftime('%Y%m%d_%H%M%S')
        output_file_name_cet = os.path.join(parent_dir,f"NaroIX_Rebalancing_MinLast_{current_timestamp_cet}_IndexLevels.xlsx")
        dataframe.to_excel(output_file_name_cet, index=False, sheet_name=sheet_name)
        print(f"DataFrame saved to {output_file_name_cet}")