from typing import Dict, Any, List
import requests
from requests.auth import HTTPBasicAuth

class ArangoDBClient:
    """Client to interact with ArangoDB"""

    def __init__(self, url: str, username: str, password: str, db_name: str):
        self.url = url
        self.auth = HTTPBasicAuth(username, password)
        self.db_name = db_name

    def get_collections(self) -> List[Dict[str, Any]]:
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
        graphs_url = f"{self.url}/_db/{self.db_name}/_api/gharial"
        response = requests.get(graphs_url, auth=self.auth)
        response.raise_for_status()
        return len(response.json().get('graphs', []))

    def get_analyzers(self) -> int:
        analyzers_url = f"{self.url}/_db/{self.db_name}/_api/analyzer"
        response = requests.get(analyzers_url, auth=self.auth)
        response.raise_for_status()
        return len(response.json().get('result', []))

    def get_summary(self) -> Dict[str, Any]:
        collections = self.get_collections()
        collection_details = {col['name']: self.get_collection_details(col['name']) for col in collections}
        graphs = self.get_graphs()
        analyzers = self.get_analyzers()

        return {
            'db_name': self.db_name,
            'collection_details': collection_details,
            'total_collections': len(collections),
            'total_documents': sum(details['document_count'] for details in collection_details.values()),
            'total_indexes': sum(details['index_count'] for details in collection_details.values()),
            'total_graphs': graphs,
            'total_analyzers': analyzers
        }
