import os

import certifi
import requests
import streamlit as st
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_openai.chat_models.base import OpenAIConnectionError
from langchain_tavily import TavilySearch

os.environ["SSL_CERT_FILE"] = certifi.where()
load_dotenv(override=True)


# @tool
# def get_weather_data(city: str) -> str:
#     """Return the current weather for a city."""
#     url = "https://api.weatherstack.com/current"
#     response = requests.get(
#         url,
#         params={
#             "access_key": os.getenv("WEATHERSTACK_API_KEY"),
#             "query": city,
#         },
#         timeout=15,
#     )
#     response.raise_for_status()
#     data = response.json()
#     if "current" not in data:
#         return f"Could not retrieve weather data for {city}."

#     current = data["current"]
#     return (
#         f"The current temperature in {city} is {current['temperature']}°C with "
#         f"{current['weather_descriptions'][0]}. Humidity is at "
#         f"{current['humidity']}% and wind speed is {current['wind_speed']} km/h."
#     )


@tool
def get_weather_data(city: str) -> str:
    """Return the current weather for a city."""
    location = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "en"},
        timeout=15,
    ).json()

    if not location.get("results"):
        return f"Could not find {city}."

    place = location["results"][0]
    weather = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        },
        timeout=15,
    ).json()["current"]

    return (
        f"The current temperature in {city} is "
        f"{weather['temperature_2m']}°C. "
        f"Humidity is {weather['relative_humidity_2m']}%. "
        f"Wind speed is {weather['wind_speed_10m']} km/h."
    )


@st.cache_resource
def create_app_agent():
    """Create the agent once per Streamlit process."""
    model = ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "nvidia/nemotron-3.5-lightning:free"),
        temperature=0,
        api_key=os.getenv("OPENROUTER_API_KEY"),
        base_url="https://openrouter.ai/api/v1",
        timeout=60,
        max_retries=2,
    )
    tools = [TavilySearch(max_results=3), get_weather_data]
    return create_agent(
        model=model,
        tools=tools,
        system_prompt=(
            "You are a helpful assistant. Use the search tool when current "
            "information is needed. Always answer in caveman language."
        ),
    )


st.set_page_config(page_title="Caveman Assistant", page_icon="💬")
st.title("Caveman Assistant")
st.caption("Ask a question. Assistant answer simple.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask something..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            result = create_app_agent().invoke({"messages": st.session_state.messages})
            answer = result["messages"][-1].content
        except OpenAIConnectionError:
            answer = (
                "Assistant could not reach OpenRouter. The connection closed "
                "before a complete response arrived. Please try again."
            )
        except (KeyError, TypeError, ValueError, requests.RequestException) as error:
            answer = f"Assistant unavailable: {error}"
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
