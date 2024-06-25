import os
import pytest
from unittest.mock import patch, MagicMock
from arango_compare.arango_compare import ArangoDBClient, main

@pytest.fixture
def mock_env():
    with patch.dict(os.environ, {
        "ARANGO_URL1": "http://mockserver1:8529",
        "ARANGO_USERNAME1": "testuser1",
        "ARANGO_PASSWORD1": "testpass1",
        "ARANGO_DB_NAME1": "testdb1",
        "ARANGO_URL2": "http://mockserver2:8529",
        "ARANGO_USERNAME2": "testuser2",
        "ARANGO_PASSWORD2": "testpass2",
        "ARANGO_DB_NAME2": "testdb2",
        "ENV": "production"
    }):
        yield

@patch("requests.get")
def test_get_collections(mock_get, mock_env):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "result": [{"name": "test_collection1"}, {"name": "test_collection2"}]
    }
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    client = ArangoDBClient(
        url=os.getenv("ARANGO_URL1"),
        username=os.getenv("ARANGO_USERNAME1"),
        password=os.getenv("ARANGO_PASSWORD1"),
        db_name=os.getenv("ARANGO_DB_NAME1")
    )

    collections = client.get_collections()
    assert len(collections) == 2
    assert collections[0]["name"] == "test_collection1"
    assert collections[1]["name"] == "test_collection2"

@patch("requests.get")
def test_get_collection_details(mock_get, mock_env):
    mock_count_response = MagicMock()
    mock_count_response.json.return_value = {"count": 42}
    mock_count_response.raise_for_status = MagicMock()

    mock_index_response = MagicMock()
    mock_index_response.json.return_value = {"indexes": [{}]}
    mock_index_response.raise_for_status = MagicMock()

    mock_get.side_effect = [mock_count_response, mock_index_response]

    client = ArangoDBClient(
        url=os.getenv("ARANGO_URL1"),
        username=os.getenv("ARANGO_USERNAME1"),
        password=os.getenv("ARANGO_PASSWORD1"),
        db_name=os.getenv("ARANGO_DB_NAME1")
    )

    details = client.get_collection_details("test_collection")
    assert details["document_count"] == 42
    assert details["index_count"] == 1

@patch("builtins.print")
@patch("requests.get")
def test_main(mock_get, mock_print, mock_env):
    mock_response = MagicMock()
    mock_response.json.side_effect = [
        # First instance - get collections
        {"result": [{"name": "test_collection1"}, {"name": "test_collection2"}]},
        # First instance - get collection details
        {"count": 42},
        {"indexes": [{}]},
        {"count": 10},
        {"indexes": [{}, {}]},
        # Second instance - get collections
        {"result": [{"name": "test_collection1"}, {"name": "test_collection2"}]},
        # Second instance - get collection details
        {"count": 43},
        {"indexes": [{}]},
        {"count": 11},
        {"indexes": [{}, {}]}
    ]
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    main()
    mock_print.assert_any_call("Collection name: test_collection1, Document count: 42, Index count: 1")
    mock_print.assert_any_call("Collection name: test_collection2, Document count: 10, Index count: 2")

