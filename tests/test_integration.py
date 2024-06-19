import time
import requests
from arango_compare import ArangoDBClient

def test_arangodb_integration():
    # Wait for ArangoDB to be ready
    time.sleep(60)

    client = ArangoDBClient(
        url="http://localhost:8529",
        username="root",
        password="testpassword",
        db_name="_system"
    )

    collections = client.get_collections()
    assert isinstance(collections, list)

    # Further assertions and tests can be added here
