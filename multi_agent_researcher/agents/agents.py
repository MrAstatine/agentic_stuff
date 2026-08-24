from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools.tools import web_search, scrape_url
from dotenv import load_dotenv

load_dotenv()


# model initialization
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


# first agent is a search agent that can perform web searches
def build_search_agent():
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful research assistant."),
            (
                "human",
                "You are a research assistant that can perform web searches. You have access to the following tools: {tools}.",
            ),
            ("human", "{input}"),
        ]
    )
    output_parser = StrOutputParser()
    agent = create_agent(
        llm=llm,
        prompt=prompt,
        output_parser=output_parser,
        tools=[web_search],
    )
    return agent


# second agent is a reader agent that can read and summarize web pages
def build_reader_agent():
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful research assistant."),
            (
                "human",
                "You are a research assistant that can read and summarize web pages. You have access to the following tools: {tools}.",
            ),
            ("human", "{input}"),
        ]
    )
    output_parser = StrOutputParser()
    agent = create_agent(
        llm=llm,
        prompt=prompt,
        output_parser=output_parser,
        tools=[scrape_url],
    )
    return agent


# writer chain
writer_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful research assistant. Write clear, structured, and detailed research reports based on the information provided.",
        ),
        (
            "human",
            """Write a detailed research report based on the following information:
            Topic: {topic}
            Research Gathered: {research}
            Structure the report with an introduction, main content(minimum 3 well explained points), conclusion and Source(list all URLs found in research). Use clear headings and subheadings where appropriate.
            Be detailed and provide in-depth analysis. Ensure the report is well-organized and easy to read.
            """,
        ),
    ]
)
writer_chain = writer_prompt | llm | StrOutputParser()
