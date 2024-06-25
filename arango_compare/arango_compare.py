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

def compare_arango_collections(client1: ArangoDBClient, client2: ArangoDBClient):
    collections1 = client1.get_collections()
    collections2 = client2.get_collections()

    collection_details1 = {col['name']: client1.get_collection_details(col['name']) for col in collections1}
    collection_details2 = {col['name']: client2.get_collection_details(col['name']) for col in collections2}

    differences = []

    for collection_name, details1 in collection_details1.items():
        details2 = collection_details2.get(collection_name)
        if not details2:
            differences.append((collection_name, details1, None))
        elif details1['document_count'] != details2['document_count'] or details1['index_count'] != details2['index_count']:
            differences.append((collection_name, details1, details2))

    for collection_name, details2 in collection_details2.items():
        if collection_name not in collection_details1:
            differences.append((collection_name, None, details2))

    return differences

def main():
    # Server 1
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

    # Server 2
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

    differences = compare_arango_collections(client1, client2)

    for collection_name, details1, details2 in differences:
        if details1 and details2:
            print(f"Collection name: {collection_name}")
            print(f"  Server1 - Document count: {details1['document_count']}, Index count: {details1['index_count']}")
            print(f"  Server2 - Document count: {details2['document_count']}, Index count: {details2['index_count']}")
        elif details1:
            print(f"Collection name: {collection_name} exists only on Server1 with Document count: {details1['document_count']} and Index count: {details1['index_count']}")
        elif details2:
            print(f"Collection name: {collection_name} exists only on Server2 with Document count: {details2['document_count']} and Index count: {details2['index_count']}")

if __name__ == "__main__":
    main()
