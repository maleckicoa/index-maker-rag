import os
import sys

parent_dir = os.path.abspath(os.path.join(os.getcwd(), "../../"))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from langchain_openai import ChatOpenAI
from langchain.agents import (
    create_openai_functions_agent,
    Tool,
    AgentExecutor,
)
from langchain import hub
from chains.index_description_chain import description_vector_chain
from chains.index_cypher_chain import index_cypher_chain
from index_maker.index_maker import make_index_tool

INDEX_AGENT_MODEL = os.getenv("INDEX_AGENT_MODEL")

from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    PromptTemplate
)


tools = [

    Tool(
        name="Graph",
        func=index_cypher_chain.invoke,
        #return_direct=True,
        description="""Use this tool to find companies based on financial criteria.
        Example trigger: "Show American financial companies with high stock returns".
        If the request is vague or conversational, do not use this tool.

        If the prompt asks for a specific number of companies (for example 10), but 
        the query returns fewer companies (for example 5), make sure to mention that 
        there is fewer companies matching the given criteria


        """
    ),

    Tool(
        name="Special",
        func=description_vector_chain.invoke,
        return_direct=True,
        description="""Use this tool only when the user starts the query with the word "special".
        Example trigger: "special: companies that manufacture electric vehicles".
        If 'special' is not in the prompt, do not use this tool.

        If the usert asks for a specific number of companies (for example 10), then return the exact number of companies.
        
        Do not make up any information.
        Format the output as follows:
        **<Company Name>** (Symbol: <Symbol>) - <Summary>



        """
    ),

    Tool(
        name="Index",
        #func=make_index_tool,
        func=lambda input_text: make_index_tool(input_text.strip()) if input_text else make_index_tool(),
        return_direct=True,
        description="""Use when asked to create a historical simulation of the Index or to make an index.
        If specific tickers are mentioned in the prompt (e.g., "Make Index AAPL, MSFT"), use them as input.
        If no tickers are provided in the prompt  (e.g., "Make Index") use "" as input.
        """
    ),
]


chat_model = ChatOpenAI(
    model=INDEX_AGENT_MODEL,
    temperature=0,
)


# Create the System and Human prompt templates
system_prompt = SystemMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=[],
        template="""You are  Indexing Chatbot, an AI assistant helping the user to create a customized financial index.

        - **If the user says he/she wants to create an index, point the user to the left panel, and mention that the instructions for creating an index are there.**
        - **If the user needs help or assistance (e.g can you help me?), introduce yourself and advise the user to read the instructions in the left panel.**
        - **If the user is having a conversation about finance or index creation, try to reply in a useful maner.**
        - **If the user greets you (e.g. hi, hello) reply by using a slight variation of this sentence: 'Hello! My name is  Indexing Chatbot. How can I assist? \n\n'.**
        - **If the user askes a non-financial question (e.g. what is the weather today?) politely reply by saying that you can only respond to questions about index making**
        - **If the user writes a non-sensical prompt (e.g. n08q0 whaw0man jdbfkj), politely respond by saying that you didn't understand the prompt.**

        - **If the user asks for a suggestion of companies with certain characteristiscs, use the Graph tool.**
        - **If the user uses word "special" at the begining of the prompt use the Special tool.**
        - **If the user asks to "Make Index" with specific tickers (e.g., 'Make Index AAPL, MSFT'), use the Index tool, only use the Index tool if the prompt contains the sentence "Make Index"**
        - **When using the Index tool, if no tickers are provided in the prompt, use the tickers from the environment default.**

        - **Remember past user interactions** to provide relevant responses.
        - **Use the conversation history** to answer follow-up questions in context.
        """
    )
)

human_prompt = HumanMessagePromptTemplate(
    prompt=PromptTemplate(
        input_variables=["input"],
        template=("{input}\n\n")))

index_agent_prompt = ChatPromptTemplate(
    name="index_agent_template",
    input_variables=["agent_scratchpad", "input", "chat_history"], 
    messages=[
        system_prompt,
        MessagesPlaceholder(variable_name='chat_history', optional=True),
        human_prompt,
        MessagesPlaceholder(variable_name='agent_scratchpad')
    ],
    validate_template=False
)


index_rag_agent = create_openai_functions_agent(
    llm=chat_model,
    prompt=index_agent_prompt,
    tools=tools
)


index_rag_agent_executor = AgentExecutor(
    agent=index_rag_agent,
    tools=tools,
    return_intermediate_steps=True,
    #return_only_outputs=True,
    verbose=True,
    #memory=chat_memory
)