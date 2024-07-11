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


    def get_analyzers(self) -> List[Dict[str, Any]]:
        analyzers_url = f"{self.url}/_db/{self.db_name}/_api/analyzer"
        response = requests.get(analyzers_url, auth=self.auth)
        response.raise_for_status()
        return response.json().get('result', [])

    def get_graphs(self) -> List[Dict[str, Any]]:
        graphs_url = f"{self.url}/_db/{self.db_name}/_api/gharial"
        response = requests.get(graphs_url, auth=self.auth)
        response.raise_for_status()
        graphs_data = response.json().get('graphs', [])
        graph_details = []
        for graph in graphs_data:
            detail = {
                'name': graph['name'],
                'edge_definitions': graph['edgeDefinitions'],
                'orphan_collections': graph['orphanCollections']
            }
            graph_details.append(detail)
        return graph_details

    # def get_indexes(self) -> List[Dict[str, Any]]:
    #     all_indexes = []
    #     collections = self.get_collections()
    #     for collection in collections:
    #         collection_name = collection['name']
    #         indexes_url = f"{self.url}/_db/{self.db_name}/_api/index?collection={collection_name}"
    #         response = requests.get(indexes_url, auth=self.auth)
    #         response.raise_for_status()
    #         indexes_data = response.json().get('indexes', [])
    #         for index in indexes_data:
    #             index_detail = {
    #                 'id': index['id'],
    #                 'type': index['type'],
    #                 'fields': index.get('fields', []),
    #                 'collection': collection_name
    #             }
    #             all_indexes.append(index_detail)
    #     return all_indexes

    def get_views(self) -> List[Dict[str, Any]]:
        views_url = f"{self.url}/_db/{self.db_name}/_api/view"
        response = requests.get(views_url, auth=self.auth)
        response.raise_for_status()
        return response.json().get('result', [])


    def get_summary(self) -> Dict[str, Any]:
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

        graphs = self.get_graphs()  # Updated to use the new get_graphs method
        total_graphs = len(graphs)
        analyzers = self.get_analyzers()
        total_analyzers = len(analyzers)
        views = self.get_views()
        total_views = len(views)
        # indexes = self.get_indexes()

        return {
            'db_name': self.db_name,
            'total_collections': total_collections,
            'total_documents': total_documents,
            'total_indexes': total_indexes,
            'total_graphs': total_graphs,  # This now represents the number of graphs, not their details
            'total_analyzers': total_analyzers,
            'total_views': total_views,
            'collection_details': collection_details,
            'graphs': graphs,  # Graph details are now included here
            'analyzers': analyzers,
            'views': views
        }

    # def get_summary(self) -> Dict[str, Any]:
    #     collections = self.get_collections()
    #     total_collections = len(collections)
    #     total_documents = 0
    #     total_indexes = 0
    #     collection_details = {}
    #
    #     for collection in collections:
    #         details = self.get_collection_details(collection['name'])
    #         total_documents += details['document_count']
    #         total_indexes += details['index_count']
    #         collection_details[collection['name']] = details
    #
    #     total_graphs = self.get_graphs()
    #     analyzers = self.get_analyzers()
    #     total_analyzers = len(analyzers)
    #     views = self.get_views()
    #     total_views = len(views)
    #
    #     return {
    #         'db_name': self.db_name,
    #         'total_collections': total_collections,
    #         'total_documents': total_documents,
    #         'total_indexes': total_indexes,
    #         'total_graphs': total_graphs,
    #         'total_analyzers': total_analyzers,
    #         'total_views': total_views,
    #         'collection_details': collection_details,
    #         'analyzers': analyzers,
    #         'views': views
    #     }


