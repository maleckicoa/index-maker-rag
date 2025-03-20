import requests
import string
import time
from ordered_set import OrderedSet
import utils.db_funcs as db
import sqlite3
import pandas as pd
from dotenv import load_dotenv


def get_data(url, api_key):
    url = url.format(api_key = api_key)
    response = requests.get(url, timeout = 20)
    if response.status_code == 200:
        data = response.json()

        if len(data)>0: 
            return data
        else:
            print(f"URL: {url}")
            print(f"Length: {len(data)}")
            print(f"No data found for {url}")
            return {}
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        print(f"Error: {response.text}")
        time.sleep(60)
        data = get_data(url, api_key)
        print(data)
        return data


def get_stocks(data):
        stocks = [item for item in data if item.get("type") == "stock"]
        return stocks


def get_symbols(data):
    return [item['symbol'] for item in data]


def get_close_data(data):
    print('get_close_data')
    if data == None or len(data) == 0:
        pass
    else:
        fields = ['date', 'close', 'volume']
        return [{'symbol': data['symbol'], **{field: record[field] for field in fields if field in record}} for record in data['historical']]


def get_mcap_data(data):
    print('get_mcap_data')
    if data == None or len(data) == 0:
        pass
    else:
        fields = ['symbol', 'date', 'marketCap']
        return [{field: item[field] for field in fields} for item in data]


def get_forex_pairs(data):
    all_ccy_pairs = [item['name'] for item in data if item.get("currency") == "EUR"]
    all_ccy_pairs_clean = [f"{s.split('/')[1]}{s.split('/')[0]}" for s in all_ccy_pairs]
    return all_ccy_pairs_clean


def get_company_data(data):
    if data == None or len(data) == 0:
        return
    else:
        fields = ['symbol', 'companyName', 'country', 'currency', 'exchange', 'exchangeShortName', 'industry', 'sector', 'beta', 'price', 'volAvg', 'mktCap', 'description']
        return [{field: item[field] for field in fields} for item in data]




        
