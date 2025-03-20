################################################################s################
# INPUT PARAMETERS #############################################################
################################################################################
file_path = 'final_backtest_teq_PR.xlsx'

mcap_threshold = 1000 # MarketCap threshold for filtering companies
max_cap_value = 1     # Maximum capping value for weight
min_cap_value = 0       # Minimum capping value for weight

scenario = 29                   # Scenario for Rebalance Frequency
date_adjustment_days = 0       # Days between Selection and Rebalancing Date

first_index_date = '2014-01-01' # e.g '2019-01-02'
index_start_level = 100
initial_divisor = 1000000

save_results = True
ignore_past_dividends = True
parent_dir = "data/"

index_type_list = ['PR']
#index_type_list = ['PR', 'GTR', 'NTR']


scenarios = {
    1: {'nth_friday': 1, 'frequency': 'M'},
    2: {'nth_friday': 2, 'frequency': 'M'},
    3: {'nth_friday': 3, 'frequency': 'M'},
    4: {'nth_friday': 4, 'frequency': 'M'},
    5: {'nth_friday': -1, 'frequency': 'M'},
    6: {'nth_friday': 1, 'frequency': 'Q'},
    7: {'nth_friday': 2, 'frequency': 'Q'},
    8: {'nth_friday': 3, 'frequency': 'Q'},
    9: {'nth_friday': 4, 'frequency': 'Q'},
    10: {'nth_friday': -1, 'frequency': 'Q'},
    11: {'nth_friday': 1, 'frequency': 'Semi-Annual', 'months': [1, 7]},
    12: {'nth_friday': 2, 'frequency': 'Semi-Annual', 'months': [1, 7]},
    13: {'nth_friday': 3, 'frequency': 'Semi-Annual', 'months': [1, 7]},
    14: {'nth_friday': 4, 'frequency': 'Semi-Annual', 'months': [1, 7]},
    15: {'nth_friday': -1, 'frequency': 'Semi-Annual', 'months': [1, 7]},
    16: {'nth_friday': 1, 'frequency': 'Semi-Annual', 'months': [2, 8]},
    17: {'nth_friday': 2, 'frequency': 'Semi-Annual', 'months': [2, 8]},
    18: {'nth_friday': 3, 'frequency': 'Semi-Annual', 'months': [2, 8]},
    19: {'nth_friday': 4, 'frequency': 'Semi-Annual', 'months': [2, 8]},
    20: {'nth_friday': -1, 'frequency': 'Semi-Annual', 'months': [2, 8]},
    21: {'nth_friday': 1, 'frequency': 'Semi-Annual', 'months': [3, 9]},
    22: {'nth_friday': 2, 'frequency': 'Semi-Annual', 'months': [3, 9]},
    23: {'nth_friday': 3, 'frequency': 'Semi-Annual', 'months': [3, 9]},
    24: {'nth_friday': 4, 'frequency': 'Semi-Annual', 'months': [3, 9]},
    25: {'nth_friday': -1, 'frequency': 'Semi-Annual', 'months': [3, 9]},
    26: {'nth_friday': 1, 'frequency': 'Semi-Annual', 'months': [4, 10]},
    27: {'nth_friday': 2, 'frequency': 'Semi-Annual', 'months': [4, 10]},
    28: {'nth_friday': 3, 'frequency': 'Semi-Annual', 'months': [4, 10]},
    29: {'nth_friday': 4, 'frequency': 'Semi-Annual', 'months': [4, 10]},
    30: {'nth_friday': -1, 'frequency': 'Semi-Annual', 'months': [4, 10]},
    31: {'nth_friday': 1, 'frequency': 'Semi-Annual', 'months': [5, 11]},
    32: {'nth_friday': 2, 'frequency': 'Semi-Annual', 'months': [5, 11]},
    33: {'nth_friday': 3, 'frequency': 'Semi-Annual', 'months': [5, 11]},
    34: {'nth_friday': 4, 'frequency': 'Semi-Annual', 'months': [5, 11]},
    35: {'nth_friday': -1, 'frequency': 'Semi-Annual', 'months': [5, 11]},
    36: {'nth_friday': 1, 'frequency': 'Semi-Annual', 'months': [6, 12]},
    37: {'nth_friday': 2, 'frequency': 'Semi-Annual', 'months': [6, 12]},
    38: {'nth_friday': 3, 'frequency': 'Semi-Annual', 'months': [6, 12]},
    39: {'nth_friday': 4, 'frequency': 'Semi-Annual', 'months': [6, 12]},
    40: {'nth_friday': -1, 'frequency': 'Semi-Annual', 'months': [6, 12]},
}