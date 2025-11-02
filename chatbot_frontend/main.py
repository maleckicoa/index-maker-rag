import os
import sys 
import pickle
import requests
import streamlit as st
import pandas as pd
import numpy as np

import asyncio
import time
import pandas as pd
import httpx
import traceback

from custom_css import get_css
from utils.frontend_utils import make_df
from dotenv import load_dotenv


env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

CHATBOT_URL = os.getenv("CHATBOT_URL", "http://localhost:8080/index-rag-agent")

def get_path(relative_path):
    return os.path.abspath(os.path.join(os.path.dirname(__file__), relative_path))

# Define file paths
logo_path = get_path("../files/site-logo.png")
logo_path_small = get_path("../files/site-logo-small.png")
logo_path_small_sky = get_path("../files/site-logo-small-sky.png")
logo_path_small_blue = get_path("../files/site-logo-small-blue.png")
data_pdf_path = get_path("../files/stock_data.pdf")
stock_info_final_path = get_path("../files/stock_info_final.pkl")
industry_list_path = get_path("../chatbot_api/src/chains/")


with open(stock_info_final_path, "rb") as file:
    stock_info_final = pickle.load(file)

with open(data_pdf_path, "rb") as file:
    pdf_data = file.read()

sys.path.append(industry_list_path)
from cypher_query_examples import industries


st.set_page_config(
    page_title="Indexing Chatbot",
    page_icon=logo_path,
    layout="wide",
    initial_sidebar_state="expanded")

#st.write("DEBUG:",industries )


######################################################################################################################
######################################################################################################################
###################################################################################################################### LEFT PANEL


with st.sidebar:
    st.header("About")
    st.markdown(
        """
        Indexing Chatbot is an AI agent designed to help you create custom-tailored financial indices.
        It leverages Retrieval-Augmented Generation (RAG) to analyze both structured and unstructured (textual) financial data.
        With this chatbot you can:  
        - Obtain suggestions for your customized stock index  
        - Identify companies in niche industries to include into your index  
        - Visualize historical performance of your customized index 
        """
        , unsafe_allow_html=True 
    )
    
    st.markdown("""</br>""", unsafe_allow_html=True )
    st.header("How to use this chatbot?")
    st.markdown("""Type the prompt in the chat window on the right. Indexing Chatbot accepts **3 types of prompts:**""")
    
########################
    st.markdown("""
    <p style="color:#004280; font-size:16px; font-weight:bold;">1-General Prompts</p>
    <p><b>Goal:</b> Obtain suggestions for your customized stock index. <br>
    Prompt examples:</p>
    """, unsafe_allow_html=True)

    st.code("""  
    ▷ Suggest 10 American companies with moderate beta 
    in technology sector and 10 Chinese stocks with 
    high volatility and high trading volume in the real 
    estate sector
    
    ▷ Suggest 30 Japanese companies with high volatility 
    and high market capitalization, in the technology 
    sector
                        
    ▷ Suggest a mix of 10 American stocks with medium 
    market capitalization in comunications sector and 
    with medium trading volume
            
    ▷ Suggest 10 Chinese stocks with high volatility 
    in real estate sector and with high trading volume

    ▷ I need a mix of British stocks in energy sector 
    and German stocks in utility sector
            
    ▷ Suggest companies with folowing tickers: DRS, 
    272210.KS, AVAV
            
    ▷ Suggest a mix of Indian stocks with high market 
    capitalization in comunications sector and Chinese 
    stocks in the technology sector with high beta and 
    some Mexican companies in Energy sector
            
    ▷ Suggest a mix of 10 American stocks with high 
    volatility and 10 Chinese stocks in the technology 
    sector with high beta, along with some German 
    companies in the financial sector, and at least 
    3 Italian companies with moderate beta
            
    ▷ Suggest a mix of Indian stocks with high market 
    capitalization in comunications sector and Chinese 
    stocks in the technology sector with high beta and 
    some Mexican companies in Energy sector and highr 
    market capitalization and high trading volume
        
    """, language="text")


########################
    st.markdown("""
    <p style="color:#004280; font-size:16px; font-weight:bold;">2-Make Index Prompts</p>
    <p><b>Goal:</b> Visualize the historical performance of your custom index.</p>
    <p><b>Note:</b> Run the prompt <b>"Make Index"</b> to generate a historical simulation (This will utilize the tickers from the last prompt).</p>
    <p>Alternatively, run the <b>"Make Index"</b> prompt including specific tickers of your choice.</p>
    <p>Prompt examples:</p>
    """, unsafe_allow_html=True)


    st.code("""        
    ▷ Make Index
            
    ▷ Make Index 123, MsFt, Db, whatever, RDDT, BHVN, 
    ALAB, INOD, AMR, MSTR, WS, ACLX, CELH
    """, language="text")

########################
    st.markdown("""
    <p style="color:#004280; font-size:16px; font-weight:bold;">3-Special Prompts</p>
    <p><b>Goal:</b> Identify companies in niche industries to include into your index.</p>
    <p><b>Note:</b> This prompt must start with the word <b>"special"</b> <br>
    Prompt examples:</p>
""", unsafe_allow_html=True)

    st.code("""        
    ▷ Special: Suggest 10 companies engaged in the 
    electric vehicle manufacturing
            
    ▷ Special: Suggest 5 companies involved in the 
    production of military drones
            
    ▷ Special: Suggest 20 companies involved in 
    producing artifical hips
    """, language="text")


########################
    st.markdown("""</br>""", unsafe_allow_html=True )
    st.header("Implementation Details")
    st.markdown("""
    - Indexing Chatbot has access to financial data for ~14000 stocks from around the world with largest trading volume.  
    - Financial data available at the moment: country, sector, industry, exchange, trading volume, average return, volatility, market capitalization, and beta values
    - In addition, in order to build the indices the chatbot has access to historical stock prices, and market capitalization since 2014
    - All prices are expressed in EUR
    - Index starting level is set to 100
    - Return is an annualized price return for the last 5 years
    - Volatility is an annualized price standard deviation of the last 5 years
    - The chatbot uses a combination of OpenAI's GPT-4 and Neo4j graph database to provide the best possible answers to your queries
                
    </p>

    """, unsafe_allow_html=True)



    st.markdown("""</br>""", unsafe_allow_html=True )
    st.header("Categories Information")
    st.code(f""" 
Countries: Argentina, Australia, Austria, Azerbaijan, Bahamas, Bahrain, Bangladesh, Belgium, Bermuda, Brazil, Canada, Cayman Islands, Chile, China, Colombia, Costa Rica, Côte d'Ivoire, Cyprus, Czechia, Denmark, Finland, France, Georgia, Germany, Gibraltar, Greece, Guernsey, Hong Kong, Hungary, Iceland, India, Indonesia, Ireland, Israel, Italy, Jamaica, Japan, Jersey, Jordan, Kazakhstan, Korea, Lithuania, Luxembourg, Macao, Malaysia, Malta, Mauritius, Mexico, Monaco, Mongolia, Netherlands, New Zealand, Nigeria, Norway, Panama, Peru, Poland, Portugal, Qatar, Saudi Arabia, Singapore, South Africa, Spain, Sweden, Switzerland, Taiwan, Tanzania, Thailand, Turkey, United Arab Emirates, United Kingdom, United States of America, Uruguay, Vietbam, Virgin Islands (British), Zambia

Sectors: Basic Materials, Communication Services, Consumer Cyclical, Consumer Defensive, Energy, Financial Services, Healthcare, Industrials, Real Estate, Technology, Utilities  \n
{industries}
Exchanges: American Stock Exchange, Australian Securities Exchange, Budapest, Canadian Securities Exchange, Copenhagen, Dubai, HKSE, Iceland, International Order Book, Istanbul Stock Exchange, Jakarta Stock Exchange, Johannesburg, KOSDAQ, KSE, Kuala Lumpur, London Stock Exchange, Mexico, NASDAQ, NASDAQ Capital Market, NASDAQ Global Market, NASDAQ Global Select, NZSE, Nasdaq, National Stock Exchange of India, New York Stock Exchange, New York Stock Exchange Arca, OTC Markets EXMKT, Oslo Stock Exchange, Other OTC, Prague, Qatar, Santiago, Saudi, Shanghai, Shenzhen, Stock Exchange of Singapore, Stockholm Stock Exchange, Swiss Exchange, São Paulo, Taipei Exchange, Taiwan, Tel Aviv, Thailand, Tokyo, Toronto Stock Exchange, Toronto Stock Exchange Ventures, Warsaw Stock Exchange\n
Beta: numerical\n
Volatility categories: Very Low, Low, Medium, High, Very High\n
Market Capitalization categories: Very Low, Low, Medium, High, Very High\n
Average Trading Volume categories: Very Low, Low, Medium, High, Very High\n
Return categories: Very Low, Low, Medium, High, Very High\n

    """, language="text")



    st.markdown("""</br>""", unsafe_allow_html=True )
    st.header("Current Limitations")
    st.markdown("""
    - Only Market Cap weighted index calculation is supported at the moment 
    - Visualization of past performace is hard-coded to start from 2014
    - Index Rebalancing are hard-coded and performed every 6 months
    - No Corporate actions or dividens are included in the index calculation
    - Suggestions are limited to 30 companies per request
                
    </p>
    """, unsafe_allow_html=True)


    st.markdown("""</br>""", unsafe_allow_html=True )
    st.header("Data")
    st.markdown("""- Here you can download and view the data used""", unsafe_allow_html=True)
 
    st.download_button(
    label="Download Stock Data",
    data=pdf_data,
    file_name="stock_data.pdf",
    mime="application/pdf",
)


######################################################################################################################
######################################################################################################################
###################################################################################################################### RIGHT PANEL

col1, col2 = st.columns([1, 7])  # Adjust width ratio as needed

with col1:
    st.image(logo_path, width=100)  # Display logo

with col2:
    st.markdown(
        """
        <div style="display: flex; align-items: flex-end; height: 100px; margin-top: -5px;">
            <h1 style="margin: 0; padding: 0; line-height: 1;">Indexing Chatbot</h1>
            <span style="font-size: 14px; color: white; background-color: #ff9800; border-radius: 5px; padding: 2px 8px;  align-self: center; ">
                Beta
            </span>

        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown(get_css(), unsafe_allow_html=True) ########## CSS IMPORT

# Ensure sidebar is open by default on desktop
st.markdown("""
<script>
(function() {
    // Open sidebar by default on desktop
    if (window.innerWidth >= 768) {
        const sidebarButton = document.querySelector('button[aria-label*="sidebar"], button[aria-label*="menu"]');
        const sidebar = document.querySelector('[data-testid="stSidebar"]');
        if (sidebar && sidebar.getAttribute('aria-expanded') !== 'true') {
            // Force sidebar open
            if (sidebarButton) {
                sidebarButton.click();
            }
            // Also set it directly
            sidebar.setAttribute('aria-expanded', 'true');
            sidebar.style.transform = 'none';
        }
    }
})();
</script>
""", unsafe_allow_html=True)



st.info("""
 **I'm your index-making support tool!**

- **Find the perfect mix:** Ask me to propose a customized stock portfolio based on your unique criteria.
- **Search smarter:** Query stocks by Country, Sector, Industry, Return, Volatility, Market Cap, Trade Volume, and Beta.
- **See the big picture:** Visualize the past performance of your tailor-made index with ease.
""")

# Ensure messages history persists
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    avatar = logo_path_small_blue if message["role"] == "user" else logo_path_small_sky
    with st.chat_message(message["role"], avatar=avatar):
        if "output" in message:
            st.markdown(message["output"])
        if "df" in message:
            if isinstance(message["df"], pd.DataFrame) and not message["df"].empty:
                st.dataframe(message["df"], hide_index=True)
        if "time_series" in message:
            st.line_chart(message["time_series"])
        if "additional_text" in message:
            st.markdown(message["additional_text"])

    
if prompt := st.chat_input("What do you want to know?"):
    st.chat_message("user", avatar=logo_path_small_blue).markdown(prompt)
    st.session_state.messages.append({"role": "user", "output": prompt})

    data = {"text": prompt, "tickers": []}


    async def main():

        timer_placeholder = st.empty()
        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout = 100) as client:
                response_task = asyncio.create_task(client.post(CHATBOT_URL, json=data))

                # Display a timer while waiting for the response
                while not response_task.done():
                    elapsed_time = int(time.time() - start_time)
                    spinner_with_timer = f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;🔄 Searching for an answer... {elapsed_time} seconds elapsed"
                    timer_placeholder.markdown(    f"{spinner_with_timer}")
                    await asyncio.sleep(1)  # Update timer every second

                response = await response_task

        except Exception as e:
            timer_placeholder.empty()
            st.error("Our engine is having some difficulties with your request, try to simplify the query.")
            #st.text(f"Details: {str(e)}")
            #st.text(f"Traceback:\n{traceback.format_exc()}")
            st.stop()

        # Clear the timer display
        timer_placeholder.empty()

        # Process the response
        if response.status_code == 200:
            response_json = response.json()
            output_text = response_json.get("output", "No response received.")

            intermediate_steps = response_json.get("intermediate_steps", [])
            intermediate_steps = intermediate_steps[0] if intermediate_steps else ""
            result = response_json.get("result", "")
            tickers = response_json.get("tickers", [])
        else:
            output_text = "An error occurred while processing your message. Please try again."
            intermediate_steps = ""
            result = ""
            tickers = []

        message_data = st.empty()

        # Always append a response message
        message_data = {
            "role": "assistant",
            "output": output_text,
            "explanation": intermediate_steps,
            "result": result,
            "tickers": tickers,
        }


        if "tool='Graph'" in intermediate_steps:

            df = make_df(stock_info_final, tickers)

            additional_text_graph = "\n\n**To visualize these stock performances as an index, type 'Make Index' as your next prompt**" if not df.empty else ""
            st.chat_message("assistant", avatar=logo_path_small_sky).markdown(output_text)
            st.dataframe(df, hide_index=True)
            st.markdown(additional_text_graph)
            message_data.update({"output": output_text, "df": df, "additional_text": additional_text_graph}) # Store dataframe and additional text

        elif "tool='Special'" in intermediate_steps:

            df = make_df(stock_info_final, tickers)
            output_text = output_text['result']
            output_text = "Here are the companies that match your criteria:\n\n\n" + output_text 

            additional_text_graph = "\n\n**To visualize these stock performances as an index, type 'Make Index' as your next prompt**" if not df.empty else ""
            st.chat_message("assistant", avatar=logo_path_small_sky).markdown(output_text)
            st.dataframe(df, hide_index=True)
            st.markdown(additional_text_graph)
            message_data.update({"output": output_text, "df": df, "additional_text": additional_text_graph}) # Store dataframe and additional text

        elif "tool='Index'" in intermediate_steps:
            time_series_dict = output_text[0]
            ticker_list = output_text[1]
            removed_tickers = output_text[2]

            time_series = pd.Series(time_series_dict)
            time_series.index = pd.to_datetime(time_series.index)
            time_series.name = "Index Value"
            time_series.index.name = "Date"

            output_text = ticker_list + "\n\n" + removed_tickers
            additional_text_index = "\n\n**Here is the historical index performance since 2015**"

            st.chat_message("assistant", avatar=logo_path_small_sky).markdown(output_text)
            #st.line_chart(time_series)
            st.markdown(additional_text_index)

            message_data.update({"output": output_text, "time_series": time_series, "additional_text": additional_text_index})

        else:
            st.chat_message("assistant", avatar=logo_path_small_sky).markdown(output_text)
            message_data.update({"output": output_text})

        for message in st.session_state.messages:
            if "additional_text" in message:
                del message["additional_text"]

        st.session_state.messages.append(message_data)
        st.rerun()

    asyncio.run(main())
