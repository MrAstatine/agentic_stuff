# %%
import os
import certifi
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch as TavilySearchResults
from langsmith import Client

client = Client()

from langchain.agents import create_agent
from langchain_classic.agents import AgentExecutor
from langchain.tools import tool
import requests

# %%
os.environ["SSL_CERT_FILE"] = (
    certifi.where()
)  # this line is necessary to avoid SSL certificate verification errors when making HTTPS requests in some environments, especially when using libraries that rely on SSL/TLS for secure communication. It sets the environment variable 'SSL_CERT_FILE' to the path of the CA bundle provided by the certifi package, which contains a collection of trusted root certificates. This ensures that the application can verify the authenticity of SSL certificates presented by servers during HTTPS requests, preventing potential security issues related to untrusted or invalid certificates.
load_dotenv(override=True)
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3.5-lightning:free")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# %% [markdown]
# Set up Tavily search tool for internet search

# %%
search_tool = TavilySearchResults(max_results=3)

# %%
# search_tool.invoke("What is the capital of France?")

# %% [markdown]
# Custom function as a tool


# %%
@tool
def get_weather_data(city: str) -> str:
    """Return the current weather for a city."""
    url = f'https://api.weatherstack.com/current?access_key={os.getenv("WEATHERSTACK_API_KEY")}&query={city}'
    response = requests.get(url)
    data = response.json()
    if "current" not in data:
        return f"Could not retrieve weather data for {city}."
    return f"The current temperature in {city} is {data['current']['temperature']}°C with {data['current']['weather_descriptions'][0]}. Humidity is at {data['current']['humidity']}% and wind speed is {data['current']['wind_speed']} km/h."


# %% [markdown]
# Initialize LLM

# %%
llm = ChatOpenAI(
    model=OPENROUTER_MODEL,
    temperature=0,
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    timeout=30,
    max_retries=0,
)

# %%
"""
try:
    response = llm.invoke("What color is a sunflower? Reply in one sentence.")
    print(response.content)
except Exception as e:
    print(f"OpenRouter request failed: {type(e).__name__}: {e}")
"""

# %%
prompt = client.pull_prompt(
    "hwchase17/react", dangerously_pull_public_prompt=True
)  # dangerously_pull_public_prompt=True allows pulling public prompts without verification. Use with caution.

# %%
tools = [search_tool, get_weather_data]

# %%
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a helpful assistant. Use the search tool when current information is needed. Always answer in caveman language.",
    debug=True,
)  # debug=True enables detailed logging of the agent's actions and decisions, which is useful for debugging and understanding its behavior.

# %%
"""
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What is the capital of France?"}]}
)
response = result["messages"][-1]
print(response.content)
"""
