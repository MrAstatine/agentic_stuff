from agents.agents import (
    build_search_agent,
    build_reader_agent,
    writer_chain,
    critic_chain,
)


def run_research_pipeline(topic):
    state = {}
    print(
        f"Starting research pipeline for topic: {topic}. Searching for relevant information..."
    )
    search_agent = build_search_agent()
    search_results = search_agent.invoke(
        {
            "messages": [
                (
                    "Find recent, reliable and detailed information about the topic: "
                    + topic
                )
            ]
        }
    )
    state["search_results"] = search_results["messages"][-1].content
    print("Search results obtained. Now reading and summarizing the information...")
    reader_agent = build_reader_agent()
    reader_results = reader_agent.invoke(
        {
            "messages": [
                (
                    "user",
                    f'Based on the search results, pick the most relevant URL and scrape it for deeper content. Here are the search results: {state["search_results"]}',
                )
            ]
        }
    )
    state["scraped_content"] = reader_results["messages"][-1].content
    print("Content scraped. Now generating a research report...")
    research_combined = f'Research Report for Topic: {topic}\n\nSearch Results:\n{state["search_results"]}\n\nScraped Content:\n{state["scraped_content"]}'
    state["report"] = writer_chain.invoke(
        {"topic": topic, "research": research_combined}
    )
    print(
        "Research report generated. Now reviewing the report for quality and accuracy..."
    )
    state["feedback"] = critic_chain.invoke({"report": state["report"]})
    print("Research report reviewed. Here is the feedback:")
    print(state["feedback"])
    return state
