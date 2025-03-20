import os
import dotenv
dotenv.load_dotenv()
INDEX_QA_MODEL = os.getenv("INDEX_QA_MODEL")

#from langchain.vectorstores.neo4j_vector import Neo4jVector
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.prompts import (
    PromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
)


neo4j_vector_index_2 = Neo4jVector(
    embedding=OpenAIEmbeddings(),  # This is required but won't recompute embeddings
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    index_name="description_embeddings",          # Index name in Neo4j
)

threshold = 0.8
k=20
retriever = neo4j_vector_index_2.as_retriever(search_type="similarity", search_kwargs={"k": k}) #, "k": 10


review_template = f"""
Here is the context with documents:
{{context}}

Your job is to analyze exactly documents from the context and return the following information for each document:
- **Company Name**
- **Symbol**
- **Summary**

Please format the output as follows:

1. **<Company Name>** (Symbol: <Symbol>) - <Summary>


For example, if the question is: "List the 3 American companies in the technology sector," your output should look like this:

1. **A10 Networks, Inc.** (Symbol: ATEN) - Provides networking solutions, including application delivery controllers and security systems.

2. **SPX Technologies, Inc.** (Symbol: SPXC) - Supplies infrastructure equipment for HVAC and detection and measurement markets.

3. **SkyWater Technology, Inc.** (Symbol: SKYT) - Offers semiconductor development and manufacturing services.


IMPORTANT: Never return more companies than the number requested in the query.

### Additional Instructions:
1. Only take information from the provided context. **Do not make up any information.**
2. Ensure all output is structured exactly as shown in the example.

"""

review_system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(input_variables=["context"], template=review_template)
)

review_human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(input_variables=["question"], template="{question}")
)
messages = [review_system_prompt, review_human_prompt]

review_prompt = ChatPromptTemplate(
    input_variables=["context", "question"], messages=messages
)

description_vector_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model=INDEX_QA_MODEL, temperature=0.2), #  randomness or creativity (0-low, 1-high)
    chain_type="stuff",
    retriever=retriever
)

description_vector_chain.combine_documents_chain.llm_chain.prompt = review_prompt