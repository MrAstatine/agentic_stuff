from langchain.tools import tool
import requests
from dotenv import load_dotenv
import os
from tavily import TavilyClient
from bs4 import BeautifulSoup
from readability import Document
import trafilatura  # this is used for extracting text from HTML. used with beautifulsoup4 and readability-lxml
import re

load_dotenv()
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


@tool
def web_search(query):
    """
    Perform a web search using the Tavily API and return the results.
    """
    try:
        results = tavily_client.search(query, max_results=5)
        return results
    except Exception as e:
        return f"An error occurred while performing the web search: {str(e)}"


@tool
def scrape_url(url):
    """
    Scrape the content of a given URL and uses multiple methods to extract the main content of the page for better reliability.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
            " AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/58.0.3029.110 Safari/537.3"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Referrer": "https://www.google.com/",
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # Raise an error for bad responses
        html = response.text
        extracted_text = trafilatura.extract(
            html, include_comments=False, include_tables=False, favor_precision=True
        )
        if extracted_text and len(extracted_text.strip()) > 200:
            cleaned = re.sub(r"\s+", " ", extracted_text).strip()
            return cleaned
        doc = Document(html)
        main_content = doc.summary()
        soup = BeautifulSoup(main_content, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        if text and len(text.strip()) > 200:
            cleaned = re.sub(r"\s+", " ", text).strip()
            return cleaned
        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer", "aside"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        cleaned = re.sub(r"\s+", " ", text).strip()
        if cleaned:
            return cleaned
        return "No significant content found on the page."
    except requests.exceptions.Timeout:
        return "The request timed out while trying to access the URL."
    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
