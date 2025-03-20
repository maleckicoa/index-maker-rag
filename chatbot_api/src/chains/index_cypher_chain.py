import os
import dotenv
dotenv.load_dotenv()

from langchain.chains import GraphCypherQAChain
from langchain.prompts import PromptTemplate
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
from chains.cypher_query_examples import *

INDEX_QA_MODEL = os.getenv("INDEX_QA_MODEL")
INDEX_CYPHER_MODEL = os.getenv("INDEX_CYPHER_MODEL")


graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
)

graph.refresh_schema()



cypher_generation_template = f"""
Task:
Generate Cypher query for a Neo4j graph database.

Instructions:
Use only the provided relationship types and properties in the schema.
Do not use any other relationship types or properties that are not provided.

Schema:
{{schema}}

Note:
Do not include any explanations or apologies in your responses.
Do not respond to any questions that might ask anything other than for you to construct a Cypher statement. 
Do not include any text except the generated Cypher statement. 
Make sure the direction of the relationship is correct in your queries. 
Make sure you alias both entities and relationships properly. 
Do not run any queries that would add to or delete from the database. 
If you need to divide numbers, make sure to filter the denominator to be non zero.

Make sure to write all necessary node aliases after the WITH  statement. 
For example, if the query contains MATCH statements which define relationships between stock, country and attribute nodes,
then the WITH statement should be: WITH stock, country, attribute


Note:
By default, limit the results to 30 rows for each query, unless the user requests less than 30 rows of results.
If the user requests a mix of stocks from different countries, limit the results to 10 rows for each country.
By default, select the companies with highest yearly return, and moderate volatility, unless the user specifies otherwise.
By default, your results should be sorted by yearly return in descending order.

The database contains information about stocks, countries, sectors, industries, and attributes. 
The Stock node is most important, all other nodes and relationships revolve around the Stock node.
The Stock nodes have properties for: symbol (stock ticker), name (company name), exchange (stock exchage), yearly_return (numerical value), yearly_volatility (numerical value), market_capitalization_amount (numerical value), average_trading_volume_amount (numerical value), and beta (numerical value). 
The Country nodes have properties for: name (this is a short country symbol like US, UK or IT) and country_full_name. 

The Sector nodes have only the name property (sector names can be: Energy, Consumer Cyclical, Healthcare, Technology, Financial Services, Industrials, Consumer Defensive, Communication Services, Basic Materials, Utilities, Real Estate, NO_DATA). 
The Industry nodes have only the name property, for every sector there are multiple possible industries. Here are the industries: {industries}



The Attribute nodes have the following properties: symbol (the same as symbol property on the Stock node), market_capitalization, volatility, average_trading_volume, return.
Except for the symbol property, all other properties of the Attribute nodes are categorical and are taking only the following values: 'Very Low', 'Low', 'Medium', 'High', 'Very High'

The description nodes hold data about company description, these nodes are not relevant for Cypher queries.
The description_chunk nodes hold the same data as description nodes, but split into chunks. These nodes are not relevant for Cypher queries.


If you are asked to query for companies with a high return, always query for "High" and "Very High",
If you are asked to query for companies with a high volatility, always query for "High" and "Very High"
If you are asked to query for companies with a high trading volume, always query for "High" and "Very High",
If you are asked to query for companies with a high market cap, always query for "High" and "Very High"
If you are asked to query for companies with a low return, always query for "Low" and "Very Low",
If you are asked to query for companies with a low volatility, always query for "Low" and "Very Low",
If you are asked to query for companies with a low trading volume, always query for "Low" and "Very Low",
If you are asked to query for companies with a low market cap, always query for "Low" and "Very Low",



Cypher query examples:
{example_1}

{example_2}

{example_3}

{example_4}

{example_5}

{example_6}

{example_7}

Always create only 1 cypher query per prompt, do not make 2 queries in cases when you are supposed to use the UNION statement
All sub-queries in an UNION must have the same column names in the Return statement
If your query uses a UNION statement, each sub-query must return exactly the same columns
If you are using a WITH statement, do not forget to put all needed node aliases after the WITH statement.


Below are examples for a cypher query where multiple countries are involved and the statement UNION ALL is used:

If you are asked to suggest a mix of stocks from two countries, and some details about the companies are provided, use this query template: {example_10}

If you are asked to provide a mix of stocks from two countries, without other details provided, use this query template: {example_11}

If you are asked to provide a mix of stocks from three, four or more countries, always use this query as template:  {example_12}


Make sure to use IS NULL or IS NOT NULL when analyzing missing properties.
Never return embedding properties in your queries. 
You must never include the statement "GROUP BY" in your query. 
If you need to divide numbers, make sure to filter the denominator to be non zero.

The question is:
{{question}}
"""

cypher_generation_prompt = PromptTemplate(
    input_variables=["schema", "question"], template=cypher_generation_template
)




qa_generation_template = """You are an assistant that takes the results from a Neo4j Cypher query and simply returns the response. 
The Query Results section contains the results of a Cypher query that was generated based on a users natural language question.  
You must never doubt that information or try to use your internal knowledge to correct it. 
Always present the full results in original formal without any comments.

Query Results:
{context}


If the Query Results: is empty, say that there are no stocks that match the criteria.
Empty information looks like this: []

"""

qa_generation_prompt = PromptTemplate(
    input_variables=["context", "question"], template=qa_generation_template
)

import time
current_time = time.time()
human_readable_time = time.ctime(current_time)
word_count = len(cypher_generation_template.split())
print('Cypher Agent')
print('Human readible time', human_readable_time)
print(f"Word count: {word_count}")


index_cypher_chain= GraphCypherQAChain.from_llm(
    cypher_llm=ChatOpenAI(model = INDEX_CYPHER_MODEL, temperature=0, request_timeout=500),
    qa_llm=ChatOpenAI(model = INDEX_QA_MODEL, temperature=0, request_timeout=500),
    graph=graph,
    verbose=True,
    return_direct= True,
    qa_prompt=qa_generation_prompt,
    cypher_prompt=cypher_generation_prompt,
    validate_cypher=True,
    top_k=60,
)
