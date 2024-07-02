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

    def get_analyzers(self) -> int:
        """Fetch the count of analyzers"""
        analyzers_url = f"{self.url}/_db/{self.db_name}/_api/analyzer"
        response = requests.get(analyzers_url, auth=self.auth)
        response.raise_for_status()
        return len(response.json().get('result', []))

    def get_views(self) -> int:
        """Fetch the count of views"""
        views_url = f"{self.url}/_db/{self.db_name}/_api/view"
        response = requests.get(views_url, auth=self.auth)
        response.raise_for_status()
        return len(response.json().get('result', []))

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the database collections, documents, indexes, and graphs"""
        collections = self.get_collections()
        total_collections = len(collections)
        total_documents = 0
        total_indexes = 0
        collection_details = {}

        for collection in collections:
            details = self.get_collection_details(collection['name'])
            total_documents += details['document_count']
            total_indexes += details['index_count']
            collection_details[collection['name']] = details

        total_graphs = self.get_graphs()
        total_analyzers = self.get_analyzers()
        total_views = self.get_views()

        return {
            'total_collections': total_collections,
            'total_documents': total_documents,
            'total_indexes': total_indexes,
            'total_graphs': total_graphs,
            'total_analyzers': total_analyzers,
            'total_views': total_views,
            'collection_details': collection_details
        }

def compare_databases(summary1: Dict[str, Any], summary2: Dict[str, Any]) -> None:
    """Compare two database summaries and pretty print the results"""
    collections1 = set(summary1['collection_details'].keys())
    collections2 = set(summary2['collection_details'].keys())

    unique_to_db1 = collections1 - collections2
    unique_to_db2 = collections2 - collections1
    matching_collections = collections1 & collections2

    mismatched_collections = []

    for collection in matching_collections:
        details1 = summary1['collection_details'][collection]
        details2 = summary2['collection_details'][collection]
        if details1['document_count'] != details2['document_count'] or details1['index_count'] != details2['index_count']:
            mismatched_collections.append(collection)

    print("="*80)
    print("Summary of Differences".center(80))
    print("="*80)

    print(f"\nNumber of collections in DB1 not in DB2: {len(unique_to_db1)}")
    if unique_to_db1:
        print("Collections unique to DB1:")
        for collection in unique_to_db1:
            print(f" - {collection}")

    print(f"\nNumber of collections in DB2 not in DB1: {len(unique_to_db2)}")
    if unique_to_db2:
        print("Collections unique to DB2:")
        for collection in unique_to_db2:
            print(f" - {collection}")

    print(f"\nNumber of collections with mismatched document or index counts: {len(mismatched_collections)}")
    if mismatched_collections:
        print("Collections with mismatched counts:")
        for collection in mismatched_collections:
            print(f" - {collection}")

    print("\n" + "="*80)
    print("Overall Feature Counts".center(80))
    print("="*80)
    print(f"{'Feature':<30} {'DB1':>20} {'DB2':>20}")
    print("-"*80)
    print(f"{'Total collections':<30} {summary1['total_collections']:>20} {summary2['total_collections']:>20}")
    print(f"{'Total documents':<30} {summary1['total_documents']:>20} {summary2['total_documents']:>20}")
    print(f"{'Total indexes':<30} {summary1['total_indexes']:>20} {summary2['total_indexes']:>20}")
    print(f"{'Total graphs':<30} {summary1['total_graphs']:>20} {summary2['total_graphs']:>20}")
    print(f"{'Total analyzers':<30} {summary1['total_analyzers']:>20} {summary2['total_analyzers']:>20}")
    print(f"{'Total views':<30} {summary1['total_views']:>20} {summary2['total_views']:>20}")
    print("="*80)


if __name__ == "__main__":
    # Example usage with environment variables
    db1_config = {
        "url": os.getenv("DB1_URL", "http://localhost:8529"),
        "username": os.getenv("DB1_USERNAME", "root"),
        "password": os.getenv("DB1_PASSWORD", "password"),
        "db_name": os.getenv("DB1_NAME", "test_db1")
    }

    db2_config = {
        "url": os.getenv("DB2_URL", "http://localhost:8529"),
        "username": os.getenv("DB2_USERNAME", "root"),
        "password": os.getenv("DB2_PASSWORD", "password"),
        "db_name": os.getenv("DB2_NAME", "test_db2")
    }

    client1 = ArangoDBClient(**db1_config)
    client2 = ArangoDBClient(**db2_config)

    summary1 = client1.get_summary()
    summary2 = client2.get_summary()

    compare_databases(summary1, summary2)
