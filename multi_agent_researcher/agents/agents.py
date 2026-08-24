from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools.tools import web_search, scrape_url
from dotenv import load_dotenv
import os

load_dotenv()


# model initialization
llm = ChatOpenAI(
    model=os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini"),
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0,
)


# first agent is a search agent that can perform web searches
def build_search_agent():
    agent = create_agent(
        model=llm,
        system_prompt="You are a helpful research assistant that can perform web searches. Use the available search tool to find recent, reliable, and detailed information.",
        tools=[web_search],
    )
    return agent


# second agent is a reader agent that can read and summarize web pages
def build_reader_agent():
    agent = create_agent(
        model=llm,
        system_prompt="You are a helpful research assistant that can read and summarize web pages. Use the available scraping tool to retrieve and summarize the most relevant URL.",
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


critic_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a sharp and constructive research critic. Your task is to review research reports and provide detailed feedback on their clarity, structure, depth of analysis, and overall quality.",
        ),
        (
            "human",
            """Review the research report provided below. Provide detailed feedback on the following aspects:
    Report:{report}
    1. Clarity: Is the report clear and easy to understand? Are there any ambiguous or confusing sections?
    2. Structure: Is the report well-organized with a logical flow? Are the headings and subheadings appropriate and helpful?
    3. Depth of Analysis: Does the report provide in-depth analysis and insights? Are there areas where more detail or explanation is needed?
    4. Overall Quality: Assess the overall quality of the report. Is it comprehensive, accurate, and well-written? Are there any significant strengths or weaknesses?
    Provide specific examples from the report to support your feedback. Suggest improvements where necessary.""",
        ),
    ]
)
critic_chain = critic_prompt | llm | StrOutputParser()
