url_stock_list = "https://financialmodelingprep.com/api/v3/stock/list?apikey={api_key}"

url_ccy_info =   "https://financialmodelingprep.com/api/v3/search-ticker?query={symbol}&limit=10000&apikey={api_key}"
url_company_info = "https://financialmodelingprep.com/api/v4/company-outlook?symbol={symbol}&apikey={api_key}"
url_company_info_short = "https://financialmodelingprep.com/api/v3/profile/{symbol}?apikey={api_key}"

url_forex = "https://financialmodelingprep.com/api/v3/historical-price-full/{forex_pair}?from=2014-01-01&to=2024-12-01&apikey={api_key}"

url_all_forex_pairs = "https://financialmodelingprep.com/api/v3/symbol/available-forex-currency-pairs?apikey={api_key}"

url_hist_price = "https://financialmodelingprep.com/api/v3/historical-price-full/{symbol}?from=2014-01-01&to=2024-12-01&apikey={api_key}"

url_mcap_24 =    "https://financialmodelingprep.com/api/v3/historical-market-capitalization/{symbol}?limit=10000&from=2024-01-01&to=2024-12-01&apikey={api_key}"
url_mcap_19_24 = "https://financialmodelingprep.com/api/v3/historical-market-capitalization/{symbol}?limit=10000&from=2019-01-01&to=2024-01-01&apikey={api_key}"
url_mcap_14_19 = "https://financialmodelingprep.com/api/v3/historical-market-capitalization/{symbol}?limit=10000&from=2014-01-01&to=2019-01-01&apikey={api_key}"