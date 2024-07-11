import datetime
import os
import tempfile
from unittest import TestCase
from unittest.mock import Mock, patch
from arango_compare.client import ArangoDBClient
from arango_compare.comparator import compare_databases

class TestArangoDBClient(TestCase):

    @patch('arango_compare.client.requests.get')
    def test_get_graphs(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            'graphs': [
                {'name': 'graph1', 'edgeDefinitions': [], 'orphanCollections': []},
                {'name': 'graph2', 'edgeDefinitions': [], 'orphanCollections': []}
            ]
        }
        mock_get.return_value = mock_response

        client = ArangoDBClient('http://localhost:8529', 'root', 'password', 'test_db1')
        graph_count = client.get_graphs()

        self.assertEqual(len(graph_count), 2)
        self.assertEqual(graph_count[0]['name'], 'graph1')
        self.assertEqual(graph_count[1]['name'], 'graph2')

    @patch('arango_compare.client.requests.get')
    def test_get_summary(self, mock_get):
        mock_response_collections = Mock()
        mock_response_collections.json.return_value = {
            'result': [{'name': 'collection1'}, {'name': 'collection2'}],
            'hasMore': False
        }

        mock_response_doc_count = Mock()
        mock_response_doc_count.json.return_value = {'count': 100}

        mock_response_indexes = Mock()
        mock_response_indexes.json.return_value = {'indexes': [{'id': '1'}, {'id': '2'}]}

        mock_response_graphs = Mock()
        mock_response_graphs.json.return_value = {
            'graphs': [
                {'name': 'graph1', 'edgeDefinitions': [], 'orphanCollections': []},
                {'name': 'graph2', 'edgeDefinitions': [], 'orphanCollections': []}
            ]
        }

        mock_response_analyzers = Mock()
        mock_response_analyzers.json.return_value = {'result': [{'name': 'analyzer1'}, {'name': 'analyzer2'}]}

        mock_response_views = Mock()
        mock_response_views.json.return_value = {'result': [{'name': 'view1'}, {'name': 'view2'}]}

        mock_get.side_effect = [
            mock_response_collections, mock_response_doc_count, mock_response_indexes,
            mock_response_doc_count, mock_response_indexes, mock_response_graphs,
            mock_response_analyzers, mock_response_views
        ]

        client = ArangoDBClient('http://localhost:8529', 'root', 'password', 'test_db1')
        summary = client.get_summary()

        self.assertEqual(summary['total_collections'], 2)
        self.assertEqual(summary['total_documents'], 200)
        self.assertEqual(summary['total_indexes'], 4)
        self.assertEqual(summary['total_graphs'], 2)
        self.assertEqual(summary['total_analyzers'], 2)
        self.assertEqual(summary['total_views'], 2)

    @patch('arango_compare.comparator.print_and_write')
    def test_compare_databases(self, mock_print_and_write):
        summary1 = {
            'db_name': 'test_db1',
            'total_collections': 2,
            'total_documents': 200,
            'total_indexes': 4,
            'total_graphs': 2,
            'total_analyzers': 2,
            'total_views': 2,
            'collection_details': {
                'collection1': {'document_count': 100, 'index_count': 2},
                'collection2': {'document_count': 100, 'index_count': 2},
            },
            'analyzers': [{'name': 'analyzer1'}, {'name': 'analyzer2'}],
            'graphs': [{'name': 'graph1'}, {'name': 'graph2'}],
            'views': [{'name': 'view1'}, {'name': 'view2'}]
        }

        summary2 = {
            'db_name': 'test_db2',
            'total_collections': 3,
            'total_documents': 300,
            'total_indexes': 6,
            'total_graphs': 3,
            'total_analyzers': 3,
            'total_views': 3,
            'collection_details': {
                'collection1': {'document_count': 100, 'index_count': 2},
                'collection2': {'document_count': 100, 'index_count': 2},
                'collection3': {'document_count': 100, 'index_count': 2},
            },
            'analyzers': [{'name': 'analyzer1'}, {'name': 'analyzer3'}],
            'graphs': [{'name': 'graph1'}, {'name': 'graph3'}],
            'views': [{'name': 'view1'}, {'name': 'view3'}]
        }

        with tempfile.TemporaryDirectory() as tmpdirname:
            client1 = Mock()  # Mock client1
            client2 = Mock()  # Mock client2
            compare_databases(client1, client2, summary1, summary2, tmpdirname)

