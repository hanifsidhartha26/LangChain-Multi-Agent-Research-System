from langchain_core.tools import tool
import requests 
from dotenv import load_dotenv
import os
from rich import print
load_dotenv()
from tavily import TavilyClient
from bs4 import BeautifulSoup
from readability import Document
import trafilatura
import re



tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str) -> str:
    """
    Perform a web search using the Tavily API and return the results as a formatted string.
    """

    results = tavily.search(query=query, num_results=5)

    out = []

    for r in results['results']:
        out.append(
            f"Title: {r['title']}\nURL: {r['url']}\nSnippet: {r['content'][:300]}\n"

        )

    return "\n----\n".join(out)

@tool
def scrape_url(url: str) -> str:
    """
    Scrape and extract clean readable text content from a URL.
    Uses multiple extraction strategies (Trafilatura -> Readability -> BeautifulSoup) for reliability.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US, en;q=0.9",
        "Referer": "https://www.google.com/",
    }

    try:
        # Fetch the webpage content
        response = requests.get(
            url,
            headers=headers, 
            timeout=15
        )

        response.raise_for_status()

        html = response.text

        # --- Strategy 1: Trafilatura (Best for structured article text and main content) ---

        extracted = trafilatura.extract(
            html, 
            include_comments=False, 
            include_tables=True
            )
            

        # --- Strategy 2: Readability-lxml (Excellent fallback for cleaning messy DOMs) ---

        
        doc = Document(html)
        clean_html = doc.summary()
        soup = BeautifulSoup(clean_html, "html.parser")

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "form"
        ]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

        if text and len(text.strip()) > 200:
            cleaned = re.sub(r'\s+', ' ', text)
            return cleaned[:700]

        

        # --- Strategy 3: BeautifulSoup Fallback full page extraction ---


        soup = BeautifulSoup(html, "html.parser")
        for tag in soup([
                    "script",
                    "style",
                    "nav",
                    "footer",
                    "header",
                    "aside",
                    "form"
        ]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)

        cleaned = re.sub(r'\s+', ' ', text)

        if cleaned:
            return cleaned[:5000]


        return "could not extract meangingful content from the page"

    except requests.exceptions.Timeout:
        return "Requestee timed out while scraping the url"
    except requests.exceptions.HTTPError as e:
        return f"Network or HTTP error trying to scrape URL: {str(e)}"
    except Exception as e:
        return f"An unexpected error occurred while scraping: {str(e)}"

