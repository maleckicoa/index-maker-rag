Delete everything in the Neo4j instance
MATCH (n)
DETACH DELETE n;


Kill the process on Port
lsof -i :8080
kill -9 91850
 

Restore a file to a specific comit:
git restore --source 623d687fae25d9b786d7214cc008f70a849f195f chatbot_api/src/chains/index_cypher_chain.py 




Models Used:
---------------------------------
index_rag_agent.py
chat_model = INDEX_AGENT_MODEL

---------------------------------
index_cypher_chain.py

index_cypher_chain
    cypher_llm = INDEX_CYPHER_MODEL
    qa_llm = INDEX_QA_MODEL

---------------------------------
index_description_chain.py

description_vector_chain = INDEX_QA_MODEL






To Do:

-> Improve agent commands
-> Fix the case where LLM returns 10 results but the table has 30

-> Dynamicaly propagate the model
-> Find a way to count the Tokens
-> Change the FMP Folder name

-> Add all 14k stocks
-> Set minimum data points