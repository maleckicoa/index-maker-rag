import re
import ast
import logging  
logging.basicConfig(level=logging.INFO)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)

def parse_intermediate_steps(response):
    try:
        text = response["intermediate_steps"][0]
        match = re.search(r"'result':\s*(\[.*?\])", text)
        result_str = match.group(1)
        result_list = ast.literal_eval(result_str)
        return result_list
    except:
        return []

    
def parse_cypher_tickers(response):
    try:
        text = response["intermediate_steps"][0]
        match = re.search(r"'result':\s*(\[.*?\])", text)
        result_str = match.group(1)
        result_list = ast.literal_eval(result_str)
        ticker_list = [ticker['Symbol'] for ticker in result_list]
        return ticker_list
    except:
        return []


def parse_description_tickers(response):
    symbols = []
    result_list = response['intermediate_steps'][0]
    symbols = [symbol.strip() for symbol in re.findall(r"Symbol: ([\w\.]+)", result_list)]
    return symbols

    
def parse_tickers(response):
    res = response['input']
    if res.startswith('special'):
        return parse_description_tickers(response)
    else:   
        return parse_cypher_tickers(response)
