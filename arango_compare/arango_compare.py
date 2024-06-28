import os
import requests
from requests.auth import HTTPBasicAuth
from typing import Dict, List, Any

class ArangoDBClient:
    """Client to interact with ArangoDB"""

    def __init__(self, url: str, username: str, password: str, db_name: str):
        self.url = url
        self.auth = HTTPBasicAuth(username, password)
        self.db_name = db_name

    def get_collections(self) -> List[Dict[str, Any]]:
        """Fetch all collections with pagination"""
        collections_url = f"{self.url}/_db/{self.db_name}/_api/collection"
        all_collections = []
        has_more = True
        offset = 0
        limit = 1000  # Adjust the limit as needed

        while has_more:
            response = requests.get(collections_url, auth=self.auth, params={'offset': offset, 'limit': limit})
            response.raise_for_status()
            result = response.json()
            collections = result.get('result', [])
            all_collections.extend(collections)
            has_more = result.get('hasMore', False)
            offset += len(collections)

        return all_collections

    def get_collection_details(self, collection_name: str) -> Dict[str, Any]:
        """Fetch document and index count for a collection"""
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

    def get_graphs(self) -> int:
        """Fetch the count of graphs"""
        graphs_url = f"{self.url}/_db/{self.db_name}/_api/gharial"
        response = requests.get(graphs_url, auth=self.auth)
        response.raise_for_status()
        return len(response.json().get('graphs', []))

    def get_views(self) -> int:
        """Fetch the count of views"""
        views_url = f"{self.url}/_db/{self.db_name}/_api/view"
        response = requests.get(views_url, auth=self.auth)
        response.raise_for_status()
        return len(response.json().get('result', []))

    def get_analyzers(self) -> int:
        """Fetch the count of analyzers"""
        analyzers_url = f"{self.url}/_db/{self.db_name}/_api/analyzer"
        response = requests.get(analyzers_url, auth=self.auth)
        response.raise_for_status()
        return len(response.json().get('result', []))

    def get_queries(self) -> int:
        """Fetch the count of saved queries"""
        queries_url = f"{self.url}/_db/{self.db_name}/_api/query/properties"
        response = requests.get(queries_url, auth=self.auth)
        response.raise_for_status()
        return len(response.json().get('queries', []))

    def get_additional_details(self) -> Dict[str, int]:
        """Fetch additional details such as graph, view, analyzer, and saved query counts"""
        return {
            'graph_count': self.get_graphs(),
            'view_count': self.get_views(),
            'analyzer_count': self.get_analyzers(),
            'query_count': self.get_queries()
        }

def compare_arango_collections(client1: ArangoDBClient, client2: ArangoDBClient) -> List[Dict[str, Any]]:
    """Compare collections and additional details between two ArangoDB clients"""
    collections1 = client1.get_collections()
    collections2 = client2.get_collections()

    collection_details1 = {col['name']: client1.get_collection_details(col['name']) for col in collections1}
    collection_details2 = {col['name']: client2.get_collection_details(col['name']) for col in collections2}

    additional_details1 = client1.get_additional_details()
    additional_details2 = client2.get_additional_details()

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

    if additional_details1 != additional_details2:
        differences.append(('additional_details', additional_details1, additional_details2))

    return differences

def print_differences(differences: List[Dict[str, Any]]):
    """Print the differences found between two ArangoDB clients"""
    if not differences:
        print("No differences found between the databases.")
        return

    for collection_name, details1, details2 in differences:
        if collection_name == 'additional_details':
            print("Additional Details Differences:")
            print(f"  Server1 - Graph count: {details1['graph_count']}, View count: {details1['view_count']}, Analyzer count: {details1['analyzer_count']}, Query count: {details1['query_count']}")
            print(f"  Server2 - Graph count: {details2['graph_count']}, View count: {details2['view_count']}, Analyzer count: {details2['analyzer_count']}, Query count: {details2['query_count']}")
        elif details1 and details2:
            print(f"Collection name: {collection_name}")
            print(f"  Server1 - Document count: {details1['document_count']}, Index count: {details1['index_count']}")
            print(f"  Server2 - Document count: {details2['document_count']}, Index count: {details2['index_count']}")
        elif details1:
            print(f"Collection name: {collection_name} exists only on Server1 with Document count: {details1['document_count']} and Index count: {details1['index_count']}")
        elif details2:
            print(f"Collection name: {collection_name} exists only on Server2 with Document count: {details2['document_count']} and Index count: {details2['index_count']}")

def main():
    """Main function to compare two ArangoDB instances"""
    try:
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
        print_differences(differences)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
