# from langchain.agents import create_agent
# from langchain_openai import ChatOpenAI
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser
# # from tools import web_search, scrape_url
# from src.tools.tools import web_search, scrape_url
# from langchain_groq import ChatGroq
# import os

# from dotenv import load_dotenv

# load_dotenv()

# #model initialization
# # llm = ChatOpenAI(model = "gpt-4o-mini",temperature=0)
# from langchain_google_genai import ChatGoogleGenerativeAI

# # New Gemini setup (Gemini 2.5 Flash is incredibly fast and cheap/free)
# #llm = ChatGoogleGenerativeAI(model="gemini-3.8-flash", temperature=0.2,timeout=60.0,max_retries=5)
# llm = ChatGroq(
#     model="qwen/qwen3.8-27b",
#     temperature=0.2,
#     max_tokens = 400,
#     groq_api_key=os.getenv("GROQ_API_KEY")
# )


# #1st agent: search agent
# def build_search_agent():
#     return create_agent(
#         model=llm,
#         tools=[web_search],
        
#     )

# #2nd agent: reader agent
# def build_reader_agent():
#     return create_agent(
#         model=llm,
#         tools=[scrape_url],
        
#     )


# #writer chain
# writer_prompt = ChatPromptTemplate.from_messages([
#     ("system", " you are an expert research writer. write clear ,,s tructured and insightful reports."),
#     ("human","""

# Topic: {topic}

# Research Gathered:
# {research}

# Structured the report as:
# - Introduction
# - Key Findings (minmum 3 well explained points)
# - Conclusion
# -Sources (list all urls  found in research)

# be detailed , factual and professional
#     """),
# ])

# writer_chain = writer_prompt | llm | StrOutputParser()


# #critic chain
# critic_prompt = ChatPromptTemplate.from_messages([
#     ("system", " you are an sharp and constructive research critic  ,,be honest and specific "),
#     ("human",""" Review the reserach report below and evaluate it strictly.


# Report:
# {report}

# Respond in this exact format:

# score: X/10

# Strengths:
# - ...
# - ...

#  Areas to Improve
#  -...
#  -...

#  One line verdict:
#  ...."""),


# ])

# critic_chain = critic_prompt | llm | StrOutputParser()


#if i want use top code 
##create_agent → create_react_agent: Swapped out the legacy non-existent function with the official prebuilt graph agent compilation endpoint.
#from langgraph.prebuilt import create_react_agent


############ ###################################################################################################################################


import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from src.tools.tools import web_search, scrape_url
from langchain_groq import ChatGroq


# Load environment keys
load_dotenv()

# Dedicated Gemini model initialization
# llm = ChatGoogleGenerativeAI(
#     model="gemini-3.1-pro-preview", 
#     temperature=0.2,
#     timeout=60.0,
#     max_retries=3
# )
llm = ChatGroq(
    model="qwen/qwen3.8-27b",
    temperature=0.2,
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# Bind the tools cleanly using native method bindings to bypass LangGraph tool parsing latency
search_llm = llm.bind_tools([web_search])
reader_llm = llm.bind_tools([scrape_url])


# 1st agent: native tool-bound search worker
def build_search_agent():
    class DirectAgentWrapper:
        def invoke(self, inputs, config=None):
            msg = inputs["messages"]
            prompt = (
                "You are an expert research assistant. You must use your web_search tool to find accurate, "
                f"recent, and granular information regarding the user request: {msg[-1][1]}. "
                "Call your tool immediately, process the snippets, and output a concise factual text summary."
            )
            # Invoke the tool directly using our verified string function to prevent server processing overhead
            query_extracted = msg[-1][1]
            search_data = web_search.run(query_extracted)
            
            # Allow the LLM to parse and clean up the raw snippets
            ai_summary = llm.invoke(f"Summarize these search results for a research paper:\n\n{search_data}")
            
            class MockMessageResponse:
                def __init__(self, content):
                    self.content = content
            
            return {"messages": [MockMessageResponse(ai_summary.content)]}
            
    return DirectAgentWrapper()


# 2nd agent: native tool-bound reading worker
def build_reader_agent():
    class DirectAgentWrapper:
        def invoke(self, inputs, config=None):
            msg = inputs["messages"]
            context_block = msg[-1][1]
            
            # Automatically parse out any absolute URL present in the prompt string
            import re
            urls = re.findall(r'(https?://[^\s\)\"]+)', context_block)
            
            if urls:
                target_url = urls[0]
                scraped_text = scrape_url.run(target_url)
            else:
                scraped_text = "No valid URL link could be extracted by the reader agent."
                
            class MockMessageResponse:
                def __init__(self, content):
                    self.content = content
                    
            return {"messages": [MockMessageResponse(scraped_text)]}
            
    return DirectAgentWrapper()


# ==========================================
# 3. Writer Chain (LCEL)
# ==========================================
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert research writer. Write clear, structured, and insightful reports."),
    ("human", """
Topic: {topic}

Research Gathered:
{research}

Structure the report as:
- Introduction
- Key Findings (minimum 3 well explained points)
- Conclusion
- Sources (list all urls found in research)

Be detailed, factual, and professional.
    """),
])

writer_chain = writer_prompt | llm | StrOutputParser()


# ==========================================
# 4. Critic Chain (LCEL)
# ==========================================
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

score: X/10

Strengths:
- ...
- ...

Areas to Improve:
-...
-...

One line verdict:
...."""),
])

critic_chain = critic_prompt | llm | StrOutputParser()
