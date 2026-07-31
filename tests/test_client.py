"""Tests for the Scrapingdog SDK client.

Run with:  pytest
These tests mock all HTTP traffic with the ``responses`` library, so no real
API key or network access is required.
"""

import pytest
import responses

import scrapingdog
from scrapingdog import Client, HTTPError, ScrapingdogResults, TimeoutError

BASE = "https://api.scrapingdog.com"


def make_client():
    return Client(api_key="test-key")


def test_requires_api_key(monkeypatch):
    monkeypatch.delenv("SCRAPINGDOG_API_KEY", raising=False)
    with pytest.raises(scrapingdog.ScrapingdogError):
        Client()


def test_api_key_from_env(monkeypatch):
    monkeypatch.setenv("SCRAPINGDOG_API_KEY", "env-key")
    assert Client().api_key == "env-key"


@responses.activate
def test_scrape_returns_html():
    responses.add(
        responses.GET, f"{BASE}/scrape", body="<html>hi</html>",
        content_type="text/html", status=200,
    )
    client = make_client()
    result = client.scrape("https://example.com", dynamic=True)

    assert result == "<html>hi</html>"
    sent = responses.calls[0].request
    assert "api_key=test-key" in sent.url
    assert "dynamic=true" in sent.url          # bool normalised
    assert "url=https" in sent.url


@responses.activate
def test_google_returns_wrapped_json():
    responses.add(
        responses.GET, f"{BASE}/google",
        json={"organic_results": [{"title": "Coffee"}]},
        status=200,
    )
    result = make_client().google(query="coffee", country="us")

    assert isinstance(result, ScrapingdogResults)
    assert result["organic_results"][0]["title"] == "Coffee"
    # attribute-style access
    assert result.organic_results[0].title == "Coffee"


@responses.activate
def test_none_params_are_dropped():
    responses.add(responses.GET, f"{BASE}/google", json={}, status=200)
    make_client().google(query="x", page=None, results=None)
    assert "page=" not in responses.calls[0].request.url
    assert "results=" not in responses.calls[0].request.url


@responses.activate
def test_amazon_product_endpoint_and_defaults():
    responses.add(responses.GET, f"{BASE}/amazon/product", json={"title": "Book"}, status=200)
    make_client().amazon_product(asin="B0TEST")
    url = responses.calls[0].request.url
    assert "/amazon/product" in url
    assert "asin=B0TEST" in url
    assert "domain=com" in url


@responses.activate
def test_linkedin_uses_profile_endpoint():
    responses.add(responses.GET, f"{BASE}/profile", json={}, status=200)
    make_client().linkedin("rbranson", type="profile")
    url = responses.calls[0].request.url
    assert "/profile?" in url
    assert "id=rbranson" in url
    assert "type=profile" in url


@responses.activate
def test_nested_path_endpoints():
    for method, path, kwargs, marker in [
        ("google_maps_reviews", "google_maps/reviews", {"data_id": "0x1:0x2"}, "data_id=0x1"),
        ("x_profile", "x/profile", {"profile_id": "elonmusk"}, "profileId=elonmusk"),
        ("tiktok_post", "tiktok/post", {"username": "nba", "post_id": "72"}, "post_id=72"),
        ("google_news_v2", "google_news/v2", {"query": "f"}, "query=f"),
        ("chatgpt", "chatgpt", {"prompt": "hi"}, "prompt=hi"),
    ]:
        responses.reset()
        responses.add(responses.GET, f"{BASE}/{path}", json={}, status=200)
        getattr(make_client(), method)(**kwargs)
        url = responses.calls[0].request.url
        assert f"/{path}?" in url
        assert marker in url


@responses.activate
def test_account_endpoint():
    responses.add(responses.GET, f"{BASE}/account", json={"requestLimit": 1000}, status=200)
    result = make_client().account()
    assert result["requestLimit"] == 1000


@responses.activate
def test_http_error_raised_with_status():
    responses.add(
        responses.GET, f"{BASE}/google",
        json={"message": "Invalid API key"}, status=401,
    )
    with pytest.raises(HTTPError) as excinfo:
        make_client().google(query="x")
    assert excinfo.value.status_code == 401
    assert "Invalid API key" in str(excinfo.value)


@responses.activate
def test_timeout_raises_sdk_timeout():
    import requests

    responses.add(
        responses.GET, f"{BASE}/scrape", body=requests.exceptions.Timeout(),
    )
    with pytest.raises(TimeoutError):
        make_client().scrape("https://example.com")
