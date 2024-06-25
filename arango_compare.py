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

def main():
    is_production = os.getenv("ENV", "development") == "production"

    if is_production:
        arango_url = os.getenv("ARANGO_URL1", "http://localhost:8529")
        arango_username = os.getenv("ARANGO_USERNAME1", "root")
        arango_password = os.getenv("ARANGO_PASSWORD1", "password")
        arango_db_name = os.getenv("ARANGO_DB_NAME1", "_system")

        client = ArangoDBClient(
            url=arango_url,
            username=arango_username,
            password=arango_password,
            db_name=arango_db_name
        )

        collections = client.get_collections()
        for collection in collections:
            collection_name = collection['name']
            details = client.get_collection_details(collection_name)
            print(f"Collection name: {collection_name}, Document count: {details['document_count']}, Index count: {details['index_count']}")
    else:
        print("Skipping database connection in non-production environment")

if __name__ == "__main__":
    main()
