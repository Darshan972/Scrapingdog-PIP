"""Result containers returned by the Scrapingdog SDK."""

from __future__ import annotations


class ScrapingdogResults(dict):
    """A ``dict`` subclass for JSON responses from structured Scrapingdog APIs.

    Behaves exactly like a regular dictionary, with the added convenience of
    attribute-style access for top-level keys::

        results = client.google(query="coffee")
        results["organic_results"]   # dict access
        results.organic_results       # attribute access
    """

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    @classmethod
    def from_response(cls, data):
        """Wrap a decoded JSON payload.

        Dicts become :class:`ScrapingdogResults`, lists are returned as a list
        with any dict members wrapped, and scalars are passed through untouched.
        """
        if isinstance(data, dict):
            return cls({key: cls.from_response(value) for key, value in data.items()})
        if isinstance(data, list):
            return [cls.from_response(item) for item in data]
        return data
