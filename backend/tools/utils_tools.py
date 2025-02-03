# tools.py
import os
from langchain_community.tools.tavily_search import TavilySearchResults

def get_search_tool():
    return TavilySearchResults(max_results=2)
