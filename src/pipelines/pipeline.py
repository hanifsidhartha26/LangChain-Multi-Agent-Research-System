# from src.agents.agents import build_search_agent, build_reader_agent, writer_chain, critic_chain


# def run_research_pipeline(topic: str) -> dict:

#     state = {}

#     #search agent working
#     print("\n"+" ="*50)
#     print("step 1 - search agent is working ...")
#     print("="*50)

#     search_agent = build_search_agent()
#     search_result = search_agent.invoke({
#         "messages" : [("user", f"Find recent, reliable and detailed information about:  {topic}")]
    
#     })
#     state["search_results"] = search_result['messages'][-1].content

#     print("\n search result ", state['search_results'])




#     #reader agent working
#     print("\n"+" ="*50)
#     print("step 1 - reader agent is scaping top resouces ...")
#     print("="*50)

#     reader_agent = build_reader_agent()
#     reader_result = reader_agent.invoke({
#         "messages" : [("user", 
#                        f"Based on the following search results about  '{topic}', "
#                        f"pick the most relevant URL and scrap it is for deeper content.\n\n"
#                        f"Search Results: \n{state['search_results'][:800]}"
#         )]
#     })
#     state["scraped_content"] = reader_result['messages'][-1].content

#     print("\n scrapedcontent: \n", state['scraped_content'])



#     #step -3 ----writer chain
        
#     print("\n"+" ="*50)
#     print("step-3 -- writer is drafting the report ...")
#     print("="*50)

#     research_combined = (
#         f"SEARCH RESULTS : \n {state['search_results']} \n\n"
#         f"DETAILED SCRAPED CONTENT : \n {state['scraped_content']}"
#     )

#     state["report"] = writer_chain.invoke({
#         "topic" : topic,
#         "reserch" : research_combined
#     })

#     print("\n Final Report\n", state['report'])



#     #step -4 ----critic  chain
            
#     print("\n"+" ="*50)
#     print("step-4 -- critic is reviewing the report ...")
#     print("="*50)


#     state["feedback"] = critic_chain.invoke({
#         "report":state['report']
#     })

#     print("\n Critic Report\n", state['feedback'])

#     return state


   

from src.agents.agents import build_search_agent, build_reader_agent, writer_chain, critic_chain


def run_research_pipeline(topic: str) -> dict:

    state = {}

    #search agent working
    print("\n"+" ="*50)
    print("step 1 - search agent is working ...")
    print("="*50)

    search_agent = build_search_agent()
    # config={"recursion_limit": 5} prevents the search loop from hanging and timing out
    search_result = search_agent.invoke(
        {"messages" : [("user", f"Find recent, reliable and detailed information about: {topic}")]},
        config={"recursion_limit": 5}
    )
    state["search_results"] = search_result['messages'][-1].content

    print("\n search result ", state['search_results'])




    #reader agent working
    print("\n"+" ="*50)
    print("step 2 - reader agent is scraping top resources ...")
    print("="*50)

    reader_agent = build_reader_agent()
    # config={"recursion_limit": 5} prevents the scraping step from looping infinitely
    reader_result = reader_agent.invoke(
        {"messages" : [("user", 
                       f"Based on the following search results about '{topic}', "
                       f"pick the most relevant URL and scrape it for deeper content.\n\n"
                       f"Search Results: \n{state['search_results'][:800]}"
        )]},
        config={"recursion_limit": 5}
    )
    state["scraped_content"] = reader_result['messages'][-1].content

    print("\n scrapedcontent: \n", state['scraped_content'])



    #step -3 ----writer chain
        
    print("\n"+" ="*50)
    print("step-3 -- writer is drafting the report ...")
    print("="*50)

    # Hard cap text boundaries to prevent payload bloat crashing Gemini
    research_combined = (
        f"SEARCH RESULTS : \n {state['search_results'][:2000]} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['scraped_content'][:3000]}"
    )

    writer_response = writer_chain.invoke({
        "topic" : topic,
        "research" : research_combined
    })
    
    # Store string content cleanly regardless of output format type
    state["report"] = writer_response.content if hasattr(writer_response, "content") else writer_response

    print("\n Final Report\n", state['report'])



    #step -4 ----critic  chain
            
    print("\n"+" ="*50)
    print("step-4 -- critic is reviewing the report ...")
    print("="*50)

    critic_response = critic_chain.invoke({
        "report": state['report']
    })
    
    state["feedback"] = critic_response.content if hasattr(critic_response, "content") else critic_response

    print("\n Critic Report\n", state['feedback'])

    return state
