# Scrapingdog Python Library & Package
[![Package](https://img.shields.io/pypi/v/scrapingdog?color=green)](https://pypi.org/project/scrapingdog) [![CI](https://github.com/Darshan972/Scrapingdog-PIP/actions/workflows/ci.yml/badge.svg)](https://github.com/Darshan972/Scrapingdog-PIP/actions/workflows/ci.yml) [![Python](https://img.shields.io/pypi/pyversions/scrapingdog)](https://pypi.org/project/scrapingdog)

Integrate web scraping and search data into your AI workflow, RAG / fine-tuning, or Python application using this official-style wrapper for [Scrapingdog](https://www.scrapingdog.com).

Scrapingdog supports general web scraping (rotating & residential proxies, JavaScript rendering), Google, Google Maps, Google Shopping, Bing, Baidu, DuckDuckGo, Amazon, Walmart, eBay, App Stores, and [more](https://www.scrapingdog.com/documentation/).

Query a vast range of data at scale, including web pages, search results, product listings, flight and hotel data, job postings, social profiles, and [more](https://www.scrapingdog.com/documentation/).

## Installation

To install the `scrapingdog` package, simply run the following command:

```bash
$ pip install scrapingdog
```

Requires Python 3.8+ and depends only on `requests`.

## Simple Usage

Let's start by searching for Coffee on Google:

```python
import os
import scrapingdog

client = scrapingdog.Client(api_key=os.getenv("SCRAPINGDOG_API_KEY"))
results = client.google(query="coffee")

print(results)
```

The `results` variable now contains a `ScrapingdogResults` object, which acts just like a standard dictionary, with attribute-style access added on top (`results.organic_results`).

Scraping an arbitrary web page returns the raw HTML instead:

```python
html = client.scrape("https://example.com", dynamic=True, premium=False)
```

The Scrapingdog API key can be obtained from [scrapingdog.com/signup](https://www.scrapingdog.com/users/register/).

Environment variables are a secure, safe, and easy way to manage secrets.
 Set `export SCRAPINGDOG_API_KEY=<secret_api_key>` in your shell.
 The client reads this variable automatically when `api_key` is omitted.

### Error handling

Unsuccessful requests raise `scrapingdog.HTTPError` or `scrapingdog.TimeoutError` exceptions. The returned status code reflects the sort of error that occurred; please refer to the [Scrapingdog documentation](https://www.scrapingdog.com/documentation/) for more details.

```python
import os
import scrapingdog

# A default timeout can be set here.
client = scrapingdog.Client(api_key=os.getenv("SCRAPINGDOG_API_KEY"), timeout=10)

try:
    results = client.google(query="coffee")
except scrapingdog.HTTPError as e:
    if e.status_code == 401:   # Invalid API key
        print(e.message)
    elif e.status_code == 400: # Missing required parameter
        pass
    elif e.status_code == 429: # Exceeds the plan's throughput limit
        pass
except scrapingdog.TimeoutError as e:
    # Handle timeout
    print(f"The request timed out: {e}")
```

All exceptions inherit from `scrapingdog.ScrapingdogError`.

## Documentation

Full API documentation is [available on scrapingdog.com](https://www.scrapingdog.com/documentation/).

Every Scrapingdog scraper has a dedicated method (75 in total). Each is a thin wrapper over `client.get()`, so **any** documented query parameter can also be passed as a keyword argument — booleans are auto-converted to `true`/`false` and `None` values are dropped. For any endpoint without a named method, call `get()` directly with the path:

```python
data = client.get("google_trends", query="bitcoin", geo="US")
```

## Basic Examples in Python

### General Web Scraping
```python
import os
import scrapingdog

client = scrapingdog.Client(api_key=os.getenv("SCRAPINGDOG_API_KEY"))
html = client.scrape(
    "https://example.com",
    dynamic=True,     # render JavaScript
    premium=True,     # use premium/residential proxies
    country="us",
)
```
- API Documentation: [scrapingdog.com/web-scraping-api](https://www.scrapingdog.com/documentation/web-scraping-api/)

### Search Google
```python
import os
import scrapingdog

client = scrapingdog.Client(api_key=os.getenv("SCRAPINGDOG_API_KEY"))
results = client.google(query="coffee", country="us", results=10, page=0)
```
- API Documentation: [scrapingdog.com/google-search-api](https://www.scrapingdog.com/documentation/google-search-api/)

### Search Bing
```python
import os
import scrapingdog

client = scrapingdog.Client(api_key=os.getenv("SCRAPINGDOG_API_KEY"))
results = client.bing(query="coffee", cc="us")
```
- API Documentation: [scrapingdog.com/bing-search-api](https://www.scrapingdog.com/documentation/bing-search-api/)

### Search Baidu
```python
import os
import scrapingdog

client = scrapingdog.Client(api_key=os.getenv("SCRAPINGDOG_API_KEY"))
results = client.baidu(query="coffee")
```
- API Documentation: [scrapingdog.com/baidu-search-api](https://www.scrapingdog.com/documentation/baidu-search-api/)

### Search DuckDuckGo
```python
import os
import scrapingdog

client = scrapingdog.Client(api_key=os.getenv("SCRAPINGDOG_API_KEY"))
results = client.duckduckgo(query="coffee")
```
- API Documentation: [scrapingdog.com/duckduckgo-search-api](https://www.scrapingdog.com/documentation/duckduckgo-search-api/)

### Search Google Maps
```python
import os
import scrapingdog

client = scrapingdog.Client(api_key=os.getenv("SCRAPINGDOG_API_KEY"))
results = client.google_maps(query="pizza")
```
- API Documentation: [scrapingdog.com/google-maps-api](https://www.scrapingdog.com/documentation/google-maps-search-api/)

### Search Google Shopping
```python
import os
import scrapingdog

client = scrapingdog.Client(api_key=os.getenv("SCRAPINGDOG_API_KEY"))
results = client.google_shopping(query="shoes", country="us")
```
- API Documentation: [scrapingdog.com/google-shopping-api](https://www.scrapingdog.com/documentation/google-shopping-api/)

### Search Google News
```python
import os
import scrapingdog

client = scrapingdog.Client(api_key=os.getenv("SCRAPINGDOG_API_KEY"))
results = client.google_news(query="football", country="us")
```
- API Documentation: [scrapingdog.com/google-news-api](https://www.scrapingdog.com/documentation/google-news-search-api/)

### Search Google Scholar
```python
import os
import scrapingdog

client = scrapingdog.Client(api_key=os.getenv("SCRAPINGDOG_API_KEY"))
results = client.google_scholar(query="coffee")
```
- API Documentation: [scrapingdog.com/google-scholar-api](https://www.scrapingdog.com/documentation/google-scholar-api/)

### Search Google Jobs
```python
import os
import scrapingdog

client = scrapingdog.Client(api_key=os.getenv("SCRAPINGDOG_API_KEY"))
results = client.google_jobs(query="jobs in london")
```
- API Documentation: [scrapingdog.com/google-jobs-api](https://www.scrapingdog.com/documentation/google-jobs-api/)

### Google Trends
```python
import os
import scrapingdog

client = scrapingdog.Client(api_key=os.getenv("SCRAPINGDOG_API_KEY"))
results = client.google_trends(query="pizza,burger", data_type="TIMESERIES")
```
- API Documentation: [scrapingdog.com/google-trends-api](https://www.scrapingdog.com/documentation/google-trends-api/)

### Amazon Search
```python
import os
import scrapingdog

client = scrapingdog.Client(api_key=os.getenv("SCRAPINGDOG_API_KEY"))
results = client.amazon_search(query="spoon", domain="com", country="us", page=1)
```
- API Documentation: [scrapingdog.com/amazon-search-scraper](https://www.scrapingdog.com/documentation/amazon-search-scraper/)

### Amazon Product
```python
import os
import scrapingdog

client = scrapingdog.Client(api_key=os.getenv("SCRAPINGDOG_API_KEY"))
results = client.amazon_product(asin="B00AP877FS", domain="com", country="us")
```
- API Documentation: [scrapingdog.com/amazon-product-scraper](https://www.scrapingdog.com/documentation/amazon-product-scraper/)

### Walmart Search
```python
import os
import scrapingdog

client = scrapingdog.Client(api_key=os.getenv("SCRAPINGDOG_API_KEY"))
results = client.walmart_search(url="https://www.walmart.com/search?q=coffee")
```
- API Documentation: [scrapingdog.com/walmart-search-scraper](https://www.scrapingdog.com/documentation/walmart-search-scraper/)

### Search eBay
```python
import os
import scrapingdog

client = scrapingdog.Client(api_key=os.getenv("SCRAPINGDOG_API_KEY"))
results = client.ebay_search(url="https://www.ebay.com/sch/i.html?_nkw=coffee")
```
- API Documentation: [scrapingdog.com/ebay-search-api](https://www.scrapingdog.com/documentation/ebay-search-api/)

### Apple App Store
```python
import os
import scrapingdog

client = scrapingdog.Client(api_key=os.getenv("SCRAPINGDOG_API_KEY"))
results = client.apple_app_store(term="whatsapp", country="us", lang="en-us")
```
- API Documentation: [scrapingdog.com/apple-app-store-api](https://www.scrapingdog.com/documentation/apple-app-store-api/)

### Profile
```python
import os
import scrapingdog

client = scrapingdog.Client(api_key=os.getenv("SCRAPINGDOG_API_KEY"))
results = client.profile("rbranson", type="profile")
```
- API Documentation: [scrapingdog.com/profile-scraper-api](https://www.scrapingdog.com/documentation/profile-scraper-api/)

### YouTube
```python
import os
import scrapingdog

client = scrapingdog.Client(api_key=os.getenv("SCRAPINGDOG_API_KEY"))
results = client.youtube(channel_id="UCX6OQ3DkcsbYNE6H8uQQuVA", country="us")
```
- API Documentation: [scrapingdog.com/youtube-channel-api](https://www.scrapingdog.com/documentation/youtube-channel-api/)

### Screenshot
```python
import os
import scrapingdog

client = scrapingdog.Client(api_key=os.getenv("SCRAPINGDOG_API_KEY"))
results = client.screenshot(url="https://www.scrapingdog.com")
```
- API Documentation: [scrapingdog.com/screenshot-api](https://www.scrapingdog.com/documentation/screenshot-api/)

### Account
```python
import os
import scrapingdog

client = scrapingdog.Client(api_key=os.getenv("SCRAPINGDOG_API_KEY"))
account = client.account()  # remaining credits & plan usage
```
- API Documentation: [scrapingdog.com/account-api](https://www.scrapingdog.com/documentation/account-api/)

## Available Methods

<details>
<summary><b>All 75 endpoint methods</b> (click to expand)</summary>

**General & account:** `scrape`, `screenshot`, `account`, `webhook`

**Google Search:** `google`, `google_images`, `google_videos`, `google_shorts`, `google_news`, `google_news_v2`, `google_shopping`, `google_local`, `google_jobs`, `google_autocomplete`, `google_finance`, `google_flights`, `google_hotels`, `google_lens`, `google_product`, `google_immersive_product`, `google_ai_mode`, `google_ai_overview`, `google_ads_transparency`

**Google Maps:** `google_maps`, `google_maps_places`, `google_maps_photos`, `google_maps_posts`, `google_maps_reviews`

**Google Scholar:** `google_scholar`, `google_scholar_profiles`, `google_scholar_author`, `google_scholar_cite`

**Google Patents / Trends:** `google_patents`, `google_patents_details`, `google_trends`, `google_trends_autocomplete`, `google_trends_trending_now`

**Other search engines:** `bing`, `bing_shopping`, `baidu`, `duckduckgo`, `yelp`, `universal_search`

**Amazon:** `amazon_search`, `amazon_product`, `amazon_offers`, `amazon_reviews`, `amazon_autocomplete`

**Apple:** `apple_app_store`, `apple_product`, `apple_reviews`

**Retail:** `walmart_search`, `walmart_product`, `walmart_reviews`, `walmart_autocomplete`, `ebay_search`, `ebay_product`, `flipkart_search`, `flipkart_product`, `myntra_search`, `myntra_product`, `zillow`

**Social & professional:** `profile`, `profile_post`, `jobs`, `indeed`, `x_profile`, `x_post`, `tiktok_profile`, `tiktok_post`, `tiktok_ads`, `facebook`, `instagram`, `youtube`

**AI:** `chatgpt`

</details>

## License

MIT License.

## Contributing

Bug reports and pull requests are welcome. Once dependencies are installed (`pip install -e ".[test]"`), you can run the tests with `pytest`.

## Publishing a new release

Releases are published to PyPI automatically via GitHub Actions using
[Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (no API token
required).

1. Bump `__version__` in [`scrapingdog/__init__.py`](scrapingdog/__init__.py)
   (the single source of truth — `pyproject.toml` reads it dynamically).
2. Push a version tag — the [release workflow](.github/workflows/release.yml)
   tests, builds, and publishes to PyPI:
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

**One-time PyPI setup** (before the first release): on
[pypi.org/manage/account/publishing](https://pypi.org/manage/account/publishing/),
add a *pending publisher* with — Project: `scrapingdog`, Owner: `Darshan972`,
Repository: `Scrapingdog-PIP`, Workflow: `release.yml`, Environment: `pypi`.
