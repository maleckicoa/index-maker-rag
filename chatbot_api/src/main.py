
import os
import asyncio
import logging
from fastapi import FastAPI, HTTPException
from agents.index_rag_agent import index_rag_agent_executor
from chatbot_api.src.models.index_rag_models import IndexQueryInput, IndexQueryOutput
from chatbot_api.src.utils.utils import *
from utils.parser import parse_intermediate_steps, parse_cypher_tickers, parse_description_tickers
from dotenv import set_key, load_dotenv

script_location = os.path.abspath(__file__)
env_file_path = os.path.abspath(os.path.join(script_location, "../../../.env"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Index Maker Chatbot",
    description="Endpoints for an index maker graph RAG chatbot",
)

####   query_index_agent ---> invoke_agent_with_retry ---> index_rag_agent_executor.ainvoke
##############################################################################################

@async_retry(max_retries=2, delay=1)
async def invoke_agent_with_retry(query: str):
    """Retry the agent if a tool fails to run."""
    return await index_rag_agent_executor.ainvoke({"input": query})


@app.get("/")
async def get_status():
    return {"status": "running"}


chat_memory_store = {}

@app.post("/index-rag-agent", response_model=IndexQueryOutput)
@app.post("/index-rag-agent/", response_model=IndexQueryOutput)
async def query_index_agent(query: IndexQueryInput) -> IndexQueryOutput:
    
    user_id = "default_user" 
    if user_id not in chat_memory_store:
        chat_memory_store[user_id] = []

    try:

        # if query.text.lower() in ["reset", "new session"]:
        #     chat_history = None
        #     query_response={"output": "Conversation history cleared. How can I assist you?.",
        #                     "intermediate_steps": []}
        #     logger.info(f"RESET")
        # else:

        chat_history = chat_memory_store[user_id]

        agent_input = {
            "input": query.text,
            "chat_history": chat_history # Set to None to if you don't want the agent to use the chat history
        }
        query_response = await asyncio.wait_for(invoke_agent_with_retry(agent_input), timeout=55)

        chat_memory_store[user_id].append({"user": query.text, "agent": query_response["output"]})

    except:        
        print("Timeout occurred. Restarting Uvicorn...")

        port = 8080
        restart_application()
        kill_process_on_port(port)
        free_port(port)
        restart_uvicorn(port)

    
        query_response = {
            "output": "Our engine is having some difficulties with your request, try to simplify the query.",
            "intermediate_steps": [],
        }
        
    
    ticker_list = []
    tool = None

    if "intermediate_steps" in query_response:
        logger.info(f"INTERMEDIATE STEPS: {query_response['intermediate_steps']}")
        query_response["intermediate_steps"] = [str(s) for s in query_response["intermediate_steps"]]

        first_step = query_response["intermediate_steps"][0] if query_response["intermediate_steps"]  else ""


        if "tool='Special'" in first_step: 
            logger.info(f"SPECIAL TOOL DETECTED")
            tool = "S"

        if "tool='Index'" in first_step: 
            logger.info(f"INDEX TOOL DETECTED")
            tool = "I"

        if "tool='Graph'" in first_step: 
            logger.info(f"GRAPH TOOL DETECTED")
            tool = "G"  
    

    if tool == "I":
        load_dotenv(dotenv_path=env_file_path, override=True)
        ticker_str = os.getenv("TICKERS")
        ticker_list = ticker_str.split(",")

    if tool == "S":
        tickers = parse_description_tickers(query_response)
        if len(tickers) > 0:
            ticker_str = ",".join(tickers)
            set_key(env_file_path, "TICKERS", ticker_str)
            logger.info(f"SPECIAL - QUERY TICKERS SUCCESSFULLY SAVED TO GLOBAL ENV: {ticker_str}")

            load_dotenv(dotenv_path=env_file_path, override=True)
            ticker_str = os.getenv("TICKERS")
            ticker_list = ticker_str.split(",")

        else:
            logger.info(f"SPECIAL - NO QUERY TICKERS SAVED TO GLOBAL ENV")
    

    if tool == "G":
        tickers = parse_cypher_tickers(query_response)
        if len(tickers) > 0:
            ticker_str = ",".join(tickers)
            set_key(env_file_path, "TICKERS", ticker_str)
            logger.info(f"GRAPH - QUERY TICKERS SUCCESSFULLY SAVED TO GLOBAL ENV: {ticker_str}")

            load_dotenv(dotenv_path=env_file_path, override=True)
            ticker_str = os.getenv("TICKERS")
            ticker_list = ticker_str.split(",")

        else:
            logger.info(f"GRAPH - NO QUERY TICKERS SAVED TO GLOBAL ENV")
    

    return IndexQueryOutput(
        input=query.text,
        output=query_response['output'],
        intermediate_steps = query_response["intermediate_steps"],
        result = parse_intermediate_steps(query_response),
        tickers = ticker_list,
        memory = chat_history if chat_history else None
    )
