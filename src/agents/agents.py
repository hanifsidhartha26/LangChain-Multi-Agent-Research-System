from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_search, scrape_url
from dotenv import load_dotenv

load_dotenv()

#model initialization
llm = ChatOpenAI(model = "gpt-4o-mini",temperature=0)


#1st agent: search agent
def build_search_agent():
    return create_agent(
        model=llm,
        tools=[web_search],
        
    )

#2nd agent: reader agent
def build_reader_agent():
    return create_agent(
        model=llm,
        tools=[scrape_url],
        
    )


#writer chain
writer_prompt = ChatPromptTemplate.from_messages([
    ("system", " you are an expert research writer. write clear ,,s tructured and insightful reports."),
    ("human","""

Topic: {topic}

Research Gathered:
{research}

Structured the report as:
- Introduction
- Key Findings (minmum 3 well explained points)
- Conclusion
-Sources (list all urls  found in research)

be detailed , factual and professional
    """),
])

writer_chain = writer_prompt | llm | StrOutputParser()


#critic chain
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", " you are an sharp and constructive research critic  ,,be honest and specific "),
    ("human",""" Review the reserach report below and evaluate it strictly.


Report:
{report}

Respond in this exact format:

score: X/10

Strengths:
- ...
- ...

 Areas to Improve
 -...
 -...

 One line verdict:
 ...."""),


])

critic_chain = critic_prompt | llm | StrOutputParser()