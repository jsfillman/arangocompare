import os
import pytest
from unittest.mock import (call, patch, MagicMock)
from arango_compare.arango_compare import ArangoDBClient, compare_arango_collections, main

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

@patch("arango_compare.arango_compare.ArangoDBClient.get_collections")
@patch("arango_compare.arango_compare.ArangoDBClient.get_collection_details")
def test_compare_arango_collections(mock_get_collection_details, mock_get_collections, mock_env):
    mock_get_collections.side_effect = [
        [{"name": "test_collection1"}, {"name": "test_collection2"}],
        [{"name": "test_collection1"}, {"name": "test_collection3"}]
    ]
    mock_get_collection_details.side_effect = [
        {"document_count": 42, "index_count": 1},
        {"document_count": 10, "index_count": 2},
        {"document_count": 43, "index_count": 1},
        {"document_count": 11, "index_count": 2}
    ]

    client1 = ArangoDBClient(
        url=os.getenv("ARANGO_URL1"),
        username=os.getenv("ARANGO_USERNAME1"),
        password=os.getenv("ARANGO_PASSWORD1"),
        db_name=os.getenv("ARANGO_DB_NAME1")
    )
    client2 = ArangoDBClient(
        url=os.getenv("ARANGO_URL2"),
        username=os.getenv("ARANGO_USERNAME2"),
        password=os.getenv("ARANGO_PASSWORD2"),
        db_name=os.getenv("ARANGO_DB_NAME2")
    )

    differences = compare_arango_collections(client1, client2)
    assert len(differences) == 3
    assert differences[0] == ("test_collection1", {"document_count": 42, "index_count": 1}, {"document_count": 43, "index_count": 1})
    assert differences[1] == ("test_collection2", {"document_count": 10, "index_count": 2}, None)
    assert differences[2] == ("test_collection3", None, {"document_count": 11, "index_count": 2})

@patch("builtins.print")
@patch("arango_compare.arango_compare.compare_arango_collections")
@patch("arango_compare.arango_compare.ArangoDBClient.get_collections")
@patch("arango_compare.arango_compare.ArangoDBClient.get_collection_details")
def test_main(mock_get_collection_details, mock_get_collections, mock_compare, mock_print, mock_env):
    mock_get_collections.side_effect = [
        [{"name": "test_collection1"}, {"name": "test_collection2"}],
        [{"name": "test_collection1"}, {"name": "test_collection2"}]
    ]
    mock_get_collection_details.side_effect = [
        {"document_count": 42, "index_count": 1},
        {"document_count": 10, "index_count": 2},
        {"document_count": 43, "index_count": 1},
        {"document_count": 11, "index_count": 2}
    ]
    mock_compare.return_value = [
        ("test_collection1", {"document_count": 42, "index_count": 1}, {"document_count": 43, "index_count": 1}),
        ("test_collection2", {"document_count": 10, "index_count": 2}, {"document_count": 11, "index_count": 2})
    ]

    main()
    calls = [
        call("Collection name: test_collection1"),
        call("  Server1 - Document count: 42, Index count: 1"),
        call("  Server2 - Document count: 43, Index count: 1"),
        call("Collection name: test_collection2"),
        call("  Server1 - Document count: 10, Index count: 2"),
        call("  Server2 - Document count: 11, Index count: 2")
    ]
    mock_print.assert_has_calls(calls, any_order=True)
