"""HTTP client for the Scrapingdog API.

Every Scrapingdog scraper is exposed as a dedicated method. Each method is a
thin wrapper over :meth:`Client.get`, so any additional query parameter the API
documents can always be passed through as a keyword argument. For any endpoint
not covered by a named method, call :meth:`Client.get` directly with the path.
"""

from __future__ import annotations

import os

import requests

from .exceptions import HTTPError, ScrapingdogError, TimeoutError
from .models import ScrapingdogResults

__all__ = ["Client"]


def _clean_params(params):
    """Drop ``None`` values and normalise booleans to ``"true"``/``"false"``."""
    cleaned = {}
    for key, value in params.items():
        if value is None:
            continue
        if isinstance(value, bool):
            value = "true" if value else "false"
        cleaned[key] = value
    return cleaned


class Client:
    """A lightweight client for the Scrapingdog API.

    Args:
        api_key: Your Scrapingdog API key. Falls back to the ``SCRAPINGDOG_API_KEY``
            environment variable when omitted.
        timeout: Per-request timeout in seconds. Scrapingdog enforces a 60s server
            side limit, which is the default here.
        base_url: Override the API base URL (mostly useful for testing).
        session: An optional pre-configured ``requests.Session``.

    Example::

        import scrapingdog

        client = scrapingdog.Client(api_key="YOUR_KEY")
        html = client.scrape("https://example.com", dynamic=True)
        results = client.google(query="coffee")
    """

    DEFAULT_BASE_URL = "https://api.scrapingdog.com"

    def __init__(self, api_key=None, *, timeout=60, base_url=None, session=None):
        self.api_key = api_key or os.getenv("SCRAPINGDOG_API_KEY")
        if not self.api_key:
            raise ScrapingdogError(
                "An api_key is required. Pass api_key=... or set the "
                "SCRAPINGDOG_API_KEY environment variable."
            )
        self.timeout = timeout
        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.session = session or requests.Session()
        self.session.headers.setdefault(
            "User-Agent", "scrapingdog-python/1.0 (+https://www.scrapingdog.com)"
        )

    # =========================================================================
    # Core request machinery
    # =========================================================================

    def get(self, endpoint="scrape", params=None, **kwargs):
        """Issue a GET request against ``endpoint`` and return the parsed result.

        JSON responses are wrapped in :class:`ScrapingdogResults`; anything else
        (e.g. raw HTML from the general scraping API) is returned as ``str``.

        Args:
            endpoint: Path segment, e.g. ``"scrape"``, ``"google"``, ``"amazon/product"``.
            params: A dict of query parameters. May also be supplied as **kwargs.

        Raises:
            HTTPError: For non-2xx responses.
            TimeoutError: When the request exceeds ``timeout``.
        """
        query = dict(params or {})
        query.update(kwargs)
        query["api_key"] = self.api_key
        query = _clean_params(query)

        url = f"{self.base_url}/{endpoint.strip('/')}"

        try:
            response = self.session.get(url, params=query, timeout=self.timeout)
        except requests.exceptions.Timeout as exc:
            raise TimeoutError(f"Request to {url} timed out after {self.timeout}s") from exc
        except requests.exceptions.RequestException as exc:
            raise ScrapingdogError(str(exc)) from exc

        if not response.ok:
            raise HTTPError(
                _error_message(response),
                status_code=response.status_code,
                response=response,
            )

        content_type = response.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return ScrapingdogResults.from_response(response.json())
        return response.text

    # =========================================================================
    # General web scraping & account
    # =========================================================================

    def scrape(
        self,
        url,
        *,
        dynamic=None,
        premium=None,
        country=None,
        wait=None,
        session_number=None,
        custom_headers=None,
        ai_query=None,
        ai_extract_rules=None,
        **params,
    ):
        """General web scraping API (``/scrape``). Returns page HTML as ``str``
        (or JSON when ``ai_query``/``ai_extract_rules`` are used).

        Args:
            url: The target page URL to scrape.
            dynamic: Render JavaScript (headless browser) when ``True``.
            premium: Use premium/residential proxies when ``True``.
            country: Two-letter country code to geo-target the proxy.
            wait: Milliseconds to wait after page load (requires ``dynamic``).
            session_number: Reuse the same proxy IP across requests.
            custom_headers: Forward custom request headers when ``True``.
            ai_query: Natural-language extraction query (returns JSON).
            ai_extract_rules: JSON schema of fields to extract (returns JSON).
        """
        return self.get(
            "scrape", url=url, dynamic=dynamic, premium=premium, country=country,
            wait=wait, session_number=session_number, custom_headers=custom_headers,
            ai_query=ai_query, ai_extract_rules=ai_extract_rules, **params,
        )

    def screenshot(self, url, **params):
        """Screenshot API (``/screenshot``)."""
        return self.get("screenshot", url=url, **params)

    def account(self, **params):
        """Account API (``/account``) — remaining credits & plan usage."""
        return self.get("account", **params)

    def webhook(self, url, *, webhook_id, **params):
        """Webhook scraping API (``/webhook``) — async scrape delivered to a webhook."""
        return self.get("webhook", url=url, webhook_id=webhook_id, **params)

    # =========================================================================
    # Google Search family
    # =========================================================================

    def google(self, query, *, results=None, country=None, page=None, **params):
        """Google Search API (``/google``)."""
        return self.get(
            "google", query=query, results=results, country=country, page=page, **params
        )

    def google_images(self, query, **params):
        """Google Images API (``/google_images``)."""
        return self.get("google_images", query=query, **params)

    def google_videos(self, query, **params):
        """Google Videos API (``/google_videos``)."""
        return self.get("google_videos", query=query, **params)

    def google_shorts(self, query, **params):
        """Google Shorts API (``/google_shorts``)."""
        return self.get("google_shorts", query=query, **params)

    def google_news(self, query, *, country=None, results=None, **params):
        """Google News API (``/google_news``)."""
        return self.get(
            "google_news", query=query, country=country, results=results, **params
        )

    def google_news_v2(self, query, *, country=None, **params):
        """Google News API v2 (``/google_news/v2``)."""
        return self.get("google_news/v2", query=query, country=country, **params)

    def google_shopping(self, query, *, country=None, **params):
        """Google Shopping API (``/google_shopping``)."""
        return self.get("google_shopping", query=query, country=country, **params)

    def google_local(self, query, **params):
        """Google Local API (``/google_local``)."""
        return self.get("google_local", query=query, **params)

    def google_jobs(self, query, **params):
        """Google Jobs API (``/google_jobs``)."""
        return self.get("google_jobs", query=query, **params)

    def google_autocomplete(self, query, *, country=None, **params):
        """Google Autocomplete API (``/google_autocomplete``)."""
        return self.get("google_autocomplete", query=query, country=country, **params)

    def google_finance(self, query, **params):
        """Google Finance API (``/google_finance``)."""
        return self.get("google_finance", query=query, **params)

    def google_flights(self, departure_id, arrival_id, *, outbound_date=None, type=None, **params):  # noqa: A002
        """Google Flights API (``/google_flights``)."""
        return self.get(
            "google_flights", departure_id=departure_id, arrival_id=arrival_id,
            outbound_date=outbound_date, type=type, **params,
        )

    def google_hotels(self, query, *, check_in_date=None, check_out_date=None, **params):
        """Google Hotels API (``/google_hotels``)."""
        return self.get(
            "google_hotels", query=query, check_in_date=check_in_date,
            check_out_date=check_out_date, **params,
        )

    def google_lens(self, url, **params):
        """Google Lens API (``/google_lens``)."""
        return self.get("google_lens", url=url, **params)

    def google_product(self, product_id, *, country=None, **params):
        """Google Product API (``/google_product``)."""
        return self.get("google_product", product_id=product_id, country=country, **params)

    def google_immersive_product(self, page_token, **params):
        """Google Immersive Product API (``/google_immersive_product``)."""
        return self.get("google_immersive_product", page_token=page_token, **params)

    def google_ai_mode(self, query, **params):
        """Google AI Mode API (``/google/ai_mode``)."""
        return self.get("google/ai_mode", query=query, **params)

    def google_ai_overview(self, url, **params):
        """Google AI Overview API (``/google/ai_overview``)."""
        return self.get("google/ai_overview", url=url, **params)

    def google_ads_transparency(self, text, *, region=None, **params):
        """Google Ads Transparency API (``/google/ads_transparency``)."""
        return self.get("google/ads_transparency", text=text, region=region, **params)

    # -- Google Maps ----------------------------------------------------------

    def google_maps(self, query, **params):
        """Google Maps API (``/google_maps``)."""
        return self.get("google_maps", query=query, **params)

    def google_maps_places(self, data_id, **params):
        """Google Maps Places API (``/google_maps/places``)."""
        return self.get("google_maps/places", data_id=data_id, **params)

    def google_maps_photos(self, data_id, **params):
        """Google Maps Photos API (``/google_maps/photos``)."""
        return self.get("google_maps/photos", data_id=data_id, **params)

    def google_maps_posts(self, data_id, **params):
        """Google Maps Posts API (``/google_maps/posts``)."""
        return self.get("google_maps/posts", data_id=data_id, **params)

    def google_maps_reviews(self, data_id, **params):
        """Google Maps Reviews API (``/google_maps/reviews``)."""
        return self.get("google_maps/reviews", data_id=data_id, **params)

    # -- Google Scholar -------------------------------------------------------

    def google_scholar(self, query, **params):
        """Google Scholar API (``/google_scholar``)."""
        return self.get("google_scholar", query=query, **params)

    def google_scholar_profiles(self, mauthors, **params):
        """Google Scholar Profiles API (``/google_scholar/profiles``)."""
        return self.get("google_scholar/profiles", mauthors=mauthors, **params)

    def google_scholar_author(self, author_id, **params):
        """Google Scholar Author API (``/google_scholar/author``)."""
        return self.get("google_scholar/author", author_id=author_id, **params)

    def google_scholar_cite(self, query, **params):
        """Google Scholar Cite API (``/google_scholar/cite``)."""
        return self.get("google_scholar/cite", query=query, **params)

    # -- Google Patents -------------------------------------------------------

    def google_patents(self, **params):
        """Google Patents search API (``/google_patents``)."""
        return self.get("google_patents", **params)

    def google_patents_details(self, patent_id, **params):
        """Google Patent Details API (``/google_patents/details``)."""
        return self.get("google_patents/details", patent_id=patent_id, **params)

    # -- Google Trends --------------------------------------------------------

    def google_trends(self, query, *, data_type=None, **params):
        """Google Trends API (``/google_trends``)."""
        return self.get("google_trends", query=query, data_type=data_type, **params)

    def google_trends_autocomplete(self, query, **params):
        """Google Trends Autocomplete API (``/google_trends/autocomplete``)."""
        return self.get("google_trends/autocomplete", query=query, **params)

    def google_trends_trending_now(self, geo, **params):
        """Google Trends "Trending Now" API (``/google_trends/trending_now``)."""
        return self.get("google_trends/trending_now", geo=geo, **params)

    # =========================================================================
    # Other search engines
    # =========================================================================

    def bing(self, query, *, cc=None, **params):
        """Bing Search API (``/bing/search``)."""
        return self.get("bing/search", query=query, cc=cc, **params)

    def bing_shopping(self, query, *, cc=None, **params):
        """Bing Shopping API (``/bing/shopping``)."""
        return self.get("bing/shopping", query=query, cc=cc, **params)

    def baidu(self, query, **params):
        """Baidu Search API (``/baidu/search``)."""
        return self.get("baidu/search", query=query, **params)

    def duckduckgo(self, query, **params):
        """DuckDuckGo Search API (``/duckduckgo/search``)."""
        return self.get("duckduckgo/search", query=query, **params)

    def yelp(self, find_desc, *, find_loc=None, **params):
        """Yelp Search API (``/yelp/search``)."""
        return self.get("yelp/search", find_desc=find_desc, find_loc=find_loc, **params)

    def universal_search(self, query, *, country=None, language=None, **params):
        """Universal Search API (``/search``)."""
        return self.get("search", query=query, country=country, language=language, **params)

    # =========================================================================
    # Amazon
    # =========================================================================

    def amazon_search(self, query, *, domain="com", page=None, country=None, **params):
        """Amazon Search API (``/amazon/search``)."""
        return self.get(
            "amazon/search", query=query, domain=domain, page=page, country=country, **params
        )

    def amazon_product(self, asin, *, domain="com", country=None, **params):
        """Amazon Product API (``/amazon/product``)."""
        return self.get("amazon/product", asin=asin, domain=domain, country=country, **params)

    def amazon_offers(self, asin, *, domain="com", country=None, **params):
        """Amazon Offers API (``/amazon/offers``)."""
        return self.get("amazon/offers", asin=asin, domain=domain, country=country, **params)

    def amazon_reviews(self, asin, *, domain="com", page=None, **params):
        """Amazon Reviews API (``/amazon/reviews``)."""
        return self.get("amazon/reviews", asin=asin, domain=domain, page=page, **params)

    def amazon_autocomplete(self, prefix, *, domain="com", **params):
        """Amazon Autocomplete API (``/amazon/autocomplete``)."""
        return self.get("amazon/autocomplete", prefix=prefix, domain=domain, **params)

    # =========================================================================
    # Apple App Store
    # =========================================================================

    def apple_app_store(self, term, *, country=None, lang=None, **params):
        """Apple App Store search API (``/apple/app_store``)."""
        return self.get("apple/app_store", term=term, country=country, lang=lang, **params)

    def apple_product(self, product_id, *, country=None, **params):
        """Apple App/Product API (``/apple/product``)."""
        return self.get("apple/product", product_id=product_id, country=country, **params)

    def apple_reviews(self, product_id, *, country=None, **params):
        """Apple App Reviews API (``/apple/reviews``)."""
        return self.get("apple/reviews", product_id=product_id, country=country, **params)

    # =========================================================================
    # Walmart
    # =========================================================================

    def walmart_search(self, url, **params):
        """Walmart Search API (``/walmart/search``)."""
        return self.get("walmart/search", url=url, **params)

    def walmart_product(self, url, **params):
        """Walmart Product API (``/walmart/product``)."""
        return self.get("walmart/product", url=url, **params)

    def walmart_reviews(self, url, **params):
        """Walmart Reviews API (``/walmart/reviews``)."""
        return self.get("walmart/reviews", url=url, **params)

    def walmart_autocomplete(self, query, **params):
        """Walmart Autocomplete API (``/walmart/autocomplete``)."""
        return self.get("walmart/autocomplete", query=query, **params)

    # =========================================================================
    # Other e-commerce
    # =========================================================================

    def ebay_search(self, url, **params):
        """eBay Search API (``/ebay/search``)."""
        return self.get("ebay/search", url=url, **params)

    def ebay_product(self, url, **params):
        """eBay Product API (``/ebay/product``)."""
        return self.get("ebay/product", url=url, **params)

    def flipkart_search(self, url, **params):
        """Flipkart Search API (``/flipkart/search``)."""
        return self.get("flipkart/search", url=url, **params)

    def flipkart_product(self, url, **params):
        """Flipkart Product API (``/flipkart/product``)."""
        return self.get("flipkart/product", url=url, **params)

    def myntra_search(self, url, **params):
        """Myntra Search API (``/myntra/search``)."""
        return self.get("myntra/search", url=url, **params)

    def myntra_product(self, url, **params):
        """Myntra Product API (``/myntra/product``)."""
        return self.get("myntra/product", url=url, **params)

    def zillow(self, url, **params):
        """Zillow Scraper API (``/zillow``)."""
        return self.get("zillow", url=url, **params)

    # =========================================================================
    # Social media & professional
    # =========================================================================

    def profile(self, id, *, type="profile", **params):  # noqa: A002
        """Profile scraper API (``/profile``).

        Args:
            id: The public profile identifier (person or company).
            type: ``"profile"`` (person) or ``"company"``.
        """
        return self.get("profile", id=id, type=type, **params)

    def profile_post(self, id, **params):  # noqa: A002
        """Profile post scraper API (``/profile/post``)."""
        return self.get("profile/post", id=id, **params)

    def jobs(self, *, field=None, geoid=None, page=None, **params):
        """Jobs search API (``/jobs``)."""
        return self.get("jobs", field=field, geoid=geoid, page=page, **params)

    def indeed(self, url, **params):
        """Indeed Jobs scraper API (``/indeed``)."""
        return self.get("indeed", url=url, **params)

    def x_profile(self, profile_id, **params):
        """X (Twitter) profile scraper (``/x/profile``)."""
        return self.get("x/profile", profileId=profile_id, **params)

    def x_post(self, tweet_id, **params):
        """X (Twitter) post scraper (``/x/post``)."""
        return self.get("x/post", tweetId=tweet_id, **params)

    def tiktok_profile(self, username, **params):
        """TikTok profile scraper (``/tiktok/profile``)."""
        return self.get("tiktok/profile", username=username, **params)

    def tiktok_post(self, username, *, post_id=None, **params):
        """TikTok post scraper (``/tiktok/post``)."""
        return self.get("tiktok/post", username=username, post_id=post_id, **params)

    def tiktok_ads(self, query, **params):
        """TikTok ads scraper (``/tiktok/ads``)."""
        return self.get("tiktok/ads", query=query, **params)

    def facebook(self, username, **params):
        """Facebook scraper (``/facebook``) — profile / posts / ads via params."""
        return self.get("facebook", username=username, **params)

    def instagram(self, username, **params):
        """Instagram scraper (``/instagram``) — profile / posts via params."""
        return self.get("instagram", username=username, **params)

    def youtube(self, **params):
        """YouTube scraper (``/youtube``).

        A single endpoint covers channel, search, video, comments and
        transcripts — pass the relevant parameter, e.g. ``channel_id=...``,
        ``search=...``, ``v=...`` (video id).
        """
        return self.get("youtube", **params)

    # =========================================================================
    # AI
    # =========================================================================

    def chatgpt(self, prompt, **params):
        """ChatGPT scraper API (``/chatgpt``)."""
        return self.get("chatgpt", prompt=prompt, **params)

    def __repr__(self):
        masked = f"{self.api_key[:4]}…" if self.api_key else "None"
        return f"<scrapingdog.Client api_key={masked} base_url={self.base_url!r}>"


def _error_message(response):
    """Best-effort extraction of an error message from a failed response."""
    try:
        payload = response.json()
    except ValueError:
        return response.text or f"HTTP {response.status_code}"
    if isinstance(payload, dict):
        for key in ("message", "error", "detail"):
            if key in payload:
                return str(payload[key])
    return str(payload)
