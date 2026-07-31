"""Scrapingdog — the official-style Python SDK for the Scrapingdog API.

Basic usage::

    import scrapingdog

    client = scrapingdog.Client(api_key="YOUR_KEY")

    # General web scraping (returns HTML)
    html = client.scrape("https://example.com", dynamic=True)

    # Structured SERP APIs (return JSON)
    results = client.google(query="coffee", country="us")
"""

from __future__ import annotations

from .client import Client
from .exceptions import HTTPError, ScrapingdogError, TimeoutError
from .models import ScrapingdogResults

__version__ = "1.0.0"

__all__ = [
    "Client",
    "ScrapingdogResults",
    "ScrapingdogError",
    "HTTPError",
    "TimeoutError",
    "__version__",
]
