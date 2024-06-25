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

    def get_collection_details(self, collection_name: str) -> Dict[str, Any]:
        collection_url = f"{self.url}/_db/{self.db_name}/_api/collection/{collection_name}/count"
        response = requests.get(collection_url, auth=self.auth)
        response.raise_for_status()
        document_count = response.json().get('count', 0)

        indexes_url = f"{self.url}/_db/{self.db_name}/_api/index?collection={collection_name}"
        response = requests.get(indexes_url, auth=self.auth)
        response.raise_for_status()
        index_count = len(response.json().get('indexes', []))

        return {
            'document_count': document_count,
            'index_count': index_count
        }

def compare_collections(client1: ArangoDBClient, client2: ArangoDBClient):
    collections1 = client1.get_collections()
    collections2 = client2.get_collections()

    for collection in collections1:
        name = collection['name']
        details1 = client1.get_collection_details(name)
        details2 = client2.get_collection_details(name)

        print(f"Collection name: {name}")
        print(f"  Instance 1 - Document count: {details1['document_count']}, Index count: {details1['index_count']}")
        print(f"  Instance 2 - Document count: {details2['document_count']}, Index count: {details2['index_count']}")

def main():
    is_production = os.getenv("ENV", "development") == "production"

    if is_production:
        # Instance 1
        arango_url1 = os.getenv("ARANGO_URL1", "http://localhost:8529")
        arango_username1 = os.getenv("ARANGO_USERNAME1", "root")
        arango_password1 = os.getenv("ARANGO_PASSWORD1", "password")
        arango_db_name1 = os.getenv("ARANGO_DB_NAME1", "_system")

        client1 = ArangoDBClient(
            url=arango_url1,
            username=arango_username1,
            password=arango_password1,
            db_name=arango_db_name1
        )

        # Instance 2
        arango_url2 = os.getenv("ARANGO_URL2", "http://localhost:8530")
        arango_username2 = os.getenv("ARANGO_USERNAME2", "root")
        arango_password2 = os.getenv("ARANGO_PASSWORD2", "password")
        arango_db_name2 = os.getenv("ARANGO_DB_NAME2", "_system")

        client2 = ArangoDBClient(
            url=arango_url2,
            username=arango_username2,
            password=arango_password2,
            db_name=arango_db_name2
        )

        compare_collections(client1, client2)
    else:
        print("Skipping database connection in non-production environment")

if __name__ == "__main__":
    main()
