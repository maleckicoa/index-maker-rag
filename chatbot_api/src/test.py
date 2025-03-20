import requests
import time
import asyncio
start_time = time.time()

print('TEST')

url = "http://127.0.0.1:800/index-rag-agent"  

inputs = "Suggest a mix of 10 european stocks with high volatility and 10 chinese stocks in technology sector with high beta and some german companies in financial sector, and at least 3 italian companies with moderate beta?"

inputs = "special:Suggest 10 european companies which are not in technology sector"

#inputs = "make index CORZ11111111, RDDT, BHVN, ALAB, INOD, AMR, MSTR, WS, ACLX, CELH, HOLO, 301165.SZ, 3896.HK, GCT, 300085.SZ, 688608.SS, 300782.SZ, 688036.SS, 688318.SS, 605111.SS, DB, STVN, ZGN, RACE"

#inputs = "make index"
#inputs = "Suggest a mix of 20 companies from Kosovo!"

#inputs = "Make Index 123, MsFt, Db, whatever,RDDT, BHVN, ALAB, INOD, AMR, MSTR, WS, ACLX, CELH,  "

#inputs = "Hello how are you"

#inputs = "Suggest 30 european companies which are in technology sector"

#inputs = "Can you help me build an index of certain companies?"

#inputs = "can you type here again the names of those companies?"

#inputs = "What is the weather like in New York?"

#inputs ="now suggest some other 2 american companies other than GEV and TLN"

#inputs = "i need a mix of chinese and american stocks in the energy sector"

#############################################################################################

# data = {"text": inputs}

# response = requests.post(url, json=data)

# for keys, values in response.json().items():
#     print(keys,values, '\n')

# end_time = time.time()
# duration = end_time - start_time
# print(f"Execution time: {duration:.2f} seconds")

#############################################################################################


import pickle

with open("files/stock_info_final.pkl", "rb") as file:
    stock_info_final = pickle.load(file)


df = stock_info_final.iloc[0:5]

print (df.columns)