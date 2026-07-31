"""Exceptions raised by the Scrapingdog Python SDK."""

from __future__ import annotations


class ScrapingdogError(Exception):
    """Base class for all errors raised by this SDK."""


class HTTPError(ScrapingdogError):
    """Raised when the Scrapingdog API returns a non-2xx response.

    Attributes:
        status_code: The HTTP status code returned by the API.
        message: A human readable description of the failure.
        response: The underlying ``requests.Response`` object (if available).
    """

    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response

    def __str__(self):
        if self.status_code is not None:
            return f"[{self.status_code}] {self.message}"
        return str(self.message)


class TimeoutError(ScrapingdogError):  # noqa: A001 - deliberately shadows builtin within package
    """Raised when a request to the Scrapingdog API times out."""
