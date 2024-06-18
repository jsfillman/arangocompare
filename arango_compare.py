import os
import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, List, Any

class ArangoDBClient:
    def __init__(self, url: str, username: str, password: str, db_name: str):
        self.url = url
        self.auth = HTTPBasicAuth(username, password)
        self.db_name = db_name

    def get_collections(self) -> List[Dict[str, Any]]:
        collections_url = f"{self.url}/_db/{self.db_name}/_api/collection"
        response = requests.get(collections_url, auth=self.auth)
        response.raise_for_status()
        return response.json().get('result', [])

def main():
    # Get connection settings from environment variables
    arango_url = os.getenv("ARANGO_URL1", "http://localhost:8529")
    arango_username = os.getenv("ARANGO_USERNAME1", "root")
    arango_password = os.getenv("ARANGO_PASSWORD1", "password")
    arango_db_name = os.getenv("ARANGO_DB_NAME1", "_system")

    # Initialize the client with the server details
    client = ArangoDBClient(
        url=arango_url,
        username=arango_username,
        password=arango_password,
        db_name=arango_db_name
    )

    collections = client.get_collections()
    for collection in collections:
        print(f"Collection name: {collection['name']}")

if __name__ == "__main__":
    main()
