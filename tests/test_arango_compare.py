import pytest
import requests
from typing import Any, Dict
from requests.auth import HTTPBasicAuth
from arango_compare import ArangoDBClient

class MockResponse:
    """A mock response object to simulate `requests.Response`."""

    @staticmethod
    def json() -> Dict[str, Any]:
        """Return a mock JSON response."""
        return {
            "result": [
                {"name": "collection1"},
                {"name": "collection2"}
            ]
        }

    @staticmethod
    def raise_for_status() -> None:
        """Simulate a successful request with no errors."""
        pass

def test_get_collections(monkeypatch: Any) -> None:
    """Test the `get_collections` method of `ArangoDBClient`."""

    def mock_get(*args: Any, **kwargs: Any) -> MockResponse:
        """Return a mock response instead of making an actual HTTP request."""
        return MockResponse()

    # Replace `requests.get` with `mock_get`
    monkeypatch.setattr(requests, "get", mock_get)

    # Initialize the client with test server details
    client = ArangoDBClient(
        url="http://arangodb:8529",
        username="root",
        password="password",
        db_name="your_database_name"
    )

    # Call the method and check the results
    collections = client.get_collections()
    assert len(collections) == 2
    assert collections[0]['name'] == "collection1"
    assert collections[1]['name'] == "collection2"
