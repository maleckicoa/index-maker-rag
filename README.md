Index Maker is a RAG designed to build portfolios (static indices) based on user prompt
For more information see: LINK to WEBSITE


Data:
The project/agent has no recurrent ETL pipeline, 
Raw data was downloaded from the FMP finacial data provider and stored as a SQlite Database
Data was cleaned and processed and for convenience store din pickle files
DAtsa from pickle Files was uplaoded to a Neo4j Graph database, which powers the RAG



.env file with the API keys
.db file - Sqlite Database with all the FMP data
.pkl files - can be created by running the respective IPYNB scripts

.venv - create a python virtual env (python -m venv .venv)
      - activate it the virtual environment (source .venv/bin/activate)
      - run poetry install


To run the Chatbot:
    - make uvi
    - make st



