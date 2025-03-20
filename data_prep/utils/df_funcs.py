import pandas as pd
import numpy as np
from langchain.text_splitter import CharacterTextSplitter
from scipy.stats import percentileofscore

def fx_converter(df1, df2, mapping_dict):
    merged = pd.merge(df1, df2, on='date', how='inner')

    converted_data = {'date': merged['date']}
    for stock, currency in mapping_dict.items():
        if stock in df1.columns and currency in df2.columns:
            converted_data[stock] = merged[stock] / merged[currency]

    converted_df = pd.DataFrame(converted_data)
    ordered_columns = ['date'] + [col for col in df1.columns if col != 'date']
    converted_df = converted_df[ordered_columns]
    return converted_df


def transform_stock_info(stock_info, forex_rates, country_codes, stock_subset):

    text_splitter = CharacterTextSplitter(
        separator=" ",  # Use space as a delimiter
        chunk_size=300,  # Split into chunks of 30 characters
        chunk_overlap=20  # Allow 5-character overlap between chunks
    )

    stock_info['country_full_name'] = stock_info['country'].map(country_codes)
    stock_info['currency'] = stock_info['currency'].str.upper()
    stock_info['currency'] = stock_info['currency'].replace({'ILA': 'ILS', 'ZAC':'ZAR'})
    for i in ['name', 'currency', 'country', 'country_full_name', 'stock_exchange', 'exchange_short_name', 'industry', 'sector', 'description' ]:
        stock_info[i] = stock_info[i].replace("", None).fillna("NO_DATA")

    stock_info["description_chunks"] = stock_info["description"].apply(lambda x: text_splitter.split_text(x))

    latest_forex = forex_rates[forex_rates['date']== max(forex_rates['date'])]
    forex_dict = {key[-3:]: value for key, value in latest_forex.iloc[0].to_dict().items()}

    all_ccys = list(forex_dict.keys())
    stock_info_ccys = list(stock_info.currency.unique())
    excluded_ccys = list(set(stock_info_ccys) - set(all_ccys))
    stock_info = stock_info[~stock_info['currency'].isin(excluded_ccys)]  # This should be KFW and NO_DATA

    stock_info['exchange_rate_eur'] = stock_info['currency'].map(forex_dict)
    stock_info['market_cap_euro'] = stock_info['market_cap'] / stock_info['exchange_rate_eur']
    stock_info['avg_trade_vol_euro'] = (stock_info['price'] * stock_info['avg_vol'])/ stock_info['exchange_rate_eur']

    stock_info['avg_trade_vol_euro'] = stock_info['avg_trade_vol_euro'].astype(float).fillna(0)
    stock_info = stock_info.loc[stock_info.groupby("name")["avg_trade_vol_euro"].idxmax()]
    stock_info =stock_info.sort_values(by =['avg_trade_vol_euro'], ascending=False)
    stock_info = stock_info.reset_index(drop=True)

    long_stock_info = stock_info.copy()
    stock_info = stock_info.head(stock_subset)

    return stock_info, long_stock_info


def transpose_df(df, values):
    df = df.pivot(index="date", columns="symbol", values = values).reset_index()
    df.columns.name = None
    df = df.sort_values(by="date", ascending=False).reset_index(drop=True)
    return df


def remove_stocks_witn_no_recent_values(df):
    last_values = df[(df['date'] >= '2024-11-01') & (df['date'] <= '2024-11-29')]
    df_select = df.loc[:, last_values.notna().any()]
    return df_select


def remove_stocks_with_gaps(df, gap_size):
    df = df.sort_values(by='date', ascending=True).reset_index(drop=True)
    data = df.iloc[:, 1:].to_numpy() 
    column_names = df.columns[1:]  

    columns_with_nan_clusters = {}

    for col_idx in range(data.shape[1]):
        col_data = data[:, col_idx]

        first_valid_idx = np.argmax(~np.isnan(col_data)) 

        # Skip the column if it is entirely NaN
        if np.isnan(col_data[first_valid_idx]):
            columns_with_nan_clusters[column_names[col_idx]] = None
            continue

        stripped_col = col_data[first_valid_idx:]
        nan_mask = np.isnan(stripped_col)

        current_streak = 0 
        for idx, value in enumerate(nan_mask):
            if value:  
                current_streak += 1

                if current_streak > gap_size:

                    columns_with_nan_clusters[column_names[col_idx]] = first_valid_idx + idx
                    break
            else:
                current_streak = 0

    final_df = df.drop(columns=list(columns_with_nan_clusters.keys()))

    return columns_with_nan_clusters, final_df


def assign_dates(df):
    df['date'] = pd.to_datetime(df['date'])
    full_date_range = pd.date_range(start='2014-01-01', end='2024-12-01')
    full_df = pd.DataFrame({'date': full_date_range})
    merged_df = pd.merge(full_df, df, on='date', how='left')
    merged_df = merged_df.sort_values(by='date', ascending=True).reset_index(drop=True)
    return merged_df


def process_data(stock_prices, stock_mcaps, gap_size):   

    pc = remove_stocks_witn_no_recent_values(stock_prices)
    _, pc_no_gap = remove_stocks_with_gaps(pc, gap_size=gap_size)
    pc_final = assign_dates(pc_no_gap)

    pc_final_inter = pc_final.copy()
    pc_final_inter.iloc[:, 1:] = pc_final_inter.iloc[:, 1:].interpolate(method="linear", limit_direction="forward", axis=0)

    mc = remove_stocks_witn_no_recent_values(stock_mcaps)
    _, mc_no_gap = remove_stocks_with_gaps(mc, gap_size=gap_size)
    mc_final = assign_dates(mc_no_gap)

    mc_final_inter = mc_final.copy()
    mc_final_inter.iloc[:, 1:] = mc_final_inter.iloc[:, 1:].interpolate(method="linear", limit_direction="forward", axis=0)

    common_columns = pc_final_inter.columns.intersection(mc_final_inter.columns)
    pc_final_inter = pc_final_inter[common_columns]
    mc_final_inter = mc_final_inter[common_columns]

    return pc_final_inter, mc_final_inter


def make_comparison_tables(df1, df2):

    df_prices = df1.copy()
    df_market_cap = df2.copy()

    first_date_prices = {
        stock: df_prices.loc[df_prices[stock].first_valid_index(), 'date']
        if df_prices[stock].first_valid_index() is not None else None
        for stock in df_prices.columns if stock != 'date'
    }

    first_date_market_cap = {
        stock: df_market_cap.loc[df_market_cap[stock].first_valid_index(), 'date']
        if df_market_cap[stock].first_valid_index() is not None else None
        for stock in df_market_cap.columns if stock != 'date'
    }

    comparison_df = pd.DataFrame({
        'Stock': first_date_prices.keys(),
        'First_Date_Prices': first_date_prices.values(),
        'First_Date_Market_Cap': first_date_market_cap.values()
    })

    comparison_df['First_Date_Prices'] = pd.to_datetime(comparison_df['First_Date_Prices'])
    comparison_df['First_Date_Market_Cap'] = pd.to_datetime(comparison_df['First_Date_Market_Cap'])

    comparison_df['Dates_Match'] = comparison_df['First_Date_Prices'] == comparison_df['First_Date_Market_Cap']
    comparison_df['Difference_in_Days'] = ( comparison_df['First_Date_Market_Cap'] - comparison_df['First_Date_Prices'] ).dt.days

    day_diff = list(range(1,11,1))
    comparison_df_1_10 = comparison_df[(comparison_df['Dates_Match']== False) & (comparison_df['Difference_in_Days'].isin(day_diff))]
    comparison_df_10_inf = comparison_df[(comparison_df['Dates_Match']== False) & (~comparison_df['Difference_in_Days'].isin(day_diff))]

    print('Number of misaligned Stocks: ', len(comparison_df))
    print('Number of Stocks for which NaN were introduced: ', len(comparison_df_1_10))
    print('Number of Stocks dropped in both Dataframes: ', len(comparison_df_10_inf), "\n")

    return comparison_df, comparison_df_1_10, comparison_df_10_inf


def align_prices_and_mcaps(df1, df2):

    df_prices = df1.copy()
    df_market_cap = df2.copy()

    comparison_df, comparison_df_1_10, comparison_df_10_inf = make_comparison_tables(df1, df2)
    
    df_prices = df_prices.drop(columns = list(comparison_df_10_inf['Stock']))
    df_market_cap = df_market_cap.drop(columns = list(comparison_df_10_inf['Stock']))


    for index, row in comparison_df_1_10.iterrows():
        stock = row['Stock']
        cutoff_date = row['First_Date_Market_Cap']
        df_prices.loc[df_prices['date'] < cutoff_date, stock] = np.nan

    return df_prices, df_market_cap


def trim_stocks_with_little_data(df1, df2, days):

    print("Stock number before trimming: ", len(df1.columns), len(df2.columns))
    non_nan_counts = df1.count()
    result_df = pd.DataFrame({'stock': non_nan_counts.index, 'count': non_nan_counts.values})
    result_df = result_df.sort_values(by='count')
    result_df = result_df[result_df['count'] < days]

    removed_stocks = list(result_df['stock'])

    df1 = df1.drop(columns = removed_stocks)
    df2 = df2.drop(columns = removed_stocks)
    print("Stock number after trimming: ", len(df1.columns), len(df2.columns))

    return df1, df2, removed_stocks


def calculate_annualized_volatilities(df):
    df = df[df['date']>='2020-01-01'] # select the last 5 years to calculate annualized volatilities
    stocks = df.iloc[:, 1:]  
    annualized_volatilities = {}
    for stock in stocks.columns:

        prices = stocks[stock].dropna()
        daily_returns = prices.pct_change().dropna()

        daily_volatility = daily_returns.std()
        annualized_volatility = daily_volatility * np.sqrt(252)

        annualized_volatilities[stock] = annualized_volatility

    return annualized_volatilities


def calculate_number_of_price_data_points(df):
        stocks = df.iloc[:, 1:]  
        number_of_data_points = {}
        for stock in stocks.columns:
            prices = stocks[stock].dropna()
            number_of_data_points[stock] = len(prices)
    
        return number_of_data_points


def calculate_annualized_returns(df):
    df = df[df['date']>='2020-01-01'] # select the last 5 years to calculate annualized returns
    stocks = df.iloc[:, 1:] 
    annualized_returns = {}
    for stock in stocks.columns:

        prices = stocks[stock].dropna()
        daily_returns = prices.pct_change().dropna()

        geometric_mean = (1 + daily_returns).prod()**(1 / len(daily_returns)) - 1

        annualized_return = (1 + geometric_mean)**252 - 1
        annualized_returns[stock] = annualized_return

    return annualized_returns


def make_bins(data_dict):

    values = list(data_dict.values())
    mean = np.mean(values)
    std = np.std(values)
    
    percentiles =  [percentileofscore(values, v, kind='rank') for v in values]
    labels = ["Very Low", "Low", "Medium", "High", "Very High"]
    thresholds = [0, 5, 20, 80, 95, 100]
    
    bins = pd.cut(percentiles, bins=thresholds, labels=labels)
    classified_dict = {key: bins[i] for i, key in enumerate(data_dict.keys())}
    
    return classified_dict


# import polars as pl
# import sqlite3

# conn = sqlite3.connect("stocks_data.db")
# stock_prices = pl.read_database("SELECT * FROM hist_prices", connection=conn)
# stock_prices = stock_prices.sort("date", descending=True)

# stock_prices = stock_prices.pivot(
#     values="close",
#     index="date",
#     columns="symbol"
# )

# stock_prices_pandas = stock_prices.to_pandas()


country_codes = {
    'US': 'United States of America',
    'GB': 'United Kingdom of Great Britain and Northern Ireland',
    'CH': 'Switzerland',
    'ZA': 'South Africa',
    'ES': 'Spain',
    'IE': 'Ireland',
    'CN': 'China',
    'IL': 'Israel',
    'AU': 'Australia',
    'TW': 'Taiwan (Province of China)',
    'LU': 'Luxembourg',
    'RU': 'Russian Federation',
    'JE': 'Jersey',
    'NL': 'Netherlands',
    'DE': 'Germany',
    'JP': 'Japan',
    'IM': 'Isle of Man',
    'AE': 'United Arab Emirates',
    'BM': 'Bermuda',
    'KR': 'Korea (Republic of)',
    'MX': 'Mexico',
    'CA': 'Canada',
    'DK': 'Denmark',
    'UY': 'Uruguay',
    'GG': 'Guernsey',
    'HK': 'Hong Kong',
    'LT': 'Lithuania',
    'GE': 'Georgia',
    'SG': 'Singapore',
    'IN': 'India',
    'BR': 'Brazil',
    'CY': 'Cyprus',
    'TR': 'Turkey',
    'GI': 'Gibraltar',
    'MN': 'Mongolia',
    'SE': 'Sweden',
    'IT': 'Italy',
    'SA': 'Saudi Arabia',
    'KY': 'Cayman Islands',
    'VN': 'Viet Nam',
    'FR': 'France',
    'AR': 'Argentina',
    'NG': 'Nigeria',
    'BE': 'Belgium',
    'NO': 'Norway',
    'FI': 'Finland',
    'TZ': 'Tanzania, United Republic of',
    'MO': 'Macao',
    'AT': 'Austria',
    'ID': 'Indonesia',
    'MT': 'Malta',
    'TH': 'Thailand',
    'PE': 'Peru',
    'NZ': 'New Zealand',
    'MC': 'Monaco',
    'CL': 'Chile',
    'MU': 'Mauritius',
    'PL': 'Poland',
    'MY': 'Malaysia',
    'PA': 'Panama',
    'GR': 'Greece',
    'KE': 'Kenya',
    'HU': 'Hungary',
    'KZ': 'Kazakhstan',
    'CO': 'Colombia',
    'CR': 'Costa Rica',
    'VG': 'Virgin Islands (British)',
    'AZ': 'Azerbaijan',
    'QA': 'Qatar',
    'CI': "Côte d'Ivoire",
    'BS': 'Bahamas',
    'CZ': 'Czechia',
    'IS': 'Iceland',
    'TC': 'Turks and Caicos Islands',
    'PR': 'Puerto Rico',
    'JO': 'Jordan',
    'EG': 'Egypt',
    'PT': 'Portugal',
    'BD': 'Bangladesh',
    'ZM': 'Zambia',
    'BH': 'Bahrain',
    'PH': 'Philippines',
    'KH': 'Cambodia',
    'KG': 'Kyrgyzstan',
    'KW': 'Kuwait',
    'LI': 'Liechtenstein',
    'BW': 'Botswana',
    'BB': 'Barbados',
    'PG': 'Papua New Guinea',
    'UA': 'Ukraine',
    'NA': 'Namibia',
    'RO': 'Romania',
    'GL': 'Greenland',
    'EE': 'Estonia',
    'MZ': 'Mozambique',
    'SI': 'Slovenia',
    'ME': 'Montenegro',
    'MM': 'Myanmar',
    'MK': 'North Macedonia',
    'BG': 'Bulgaria',
    'AI': 'Anguilla',
    'SK': 'Slovakia',
    'SR': 'Suriname',
    'CW': 'Curaçao',
    'DO': 'Dominican Republic',
    'FK': 'Falkland Islands (Malvinas)',
    'NO_DATA': 'No Data Available'
}