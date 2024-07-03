import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch, Mock
from arango_compare.client import ArangoDBClient
from arango_compare.comparator import compare_databases

class TestArangoDBClient(unittest.TestCase):

    @patch('arango_compare.client.requests.get')
    def test_get_collections(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            'result': [{'name': 'collection1'}, {'name': 'collection2'}],
            'hasMore': False
        }
        mock_get.return_value = mock_response

        client = ArangoDBClient('http://localhost:8529', 'root', 'password', 'test_db')
        collections = client.get_collections()

        self.assertEqual(len(collections), 2)
        self.assertEqual(collections[0]['name'], 'collection1')
        self.assertEqual(collections[1]['name'], 'collection2')

    @patch('arango_compare.client.requests.get')
    def test_get_collection_details(self, mock_get):
        mock_response_doc_count = Mock()
        mock_response_doc_count.json.return_value = {'count': 100}

        mock_response_indexes = Mock()
        mock_response_indexes.json.return_value = {'indexes': [{'id': '1'}, {'id': '2'}]}

        mock_get.side_effect = [mock_response_doc_count, mock_response_indexes]

        client = ArangoDBClient('http://localhost:8529', 'root', 'password', 'test_db')
        details = client.get_collection_details('collection1')

        self.assertEqual(details['document_count'], 100)
        self.assertEqual(details['index_count'], 2)

    @patch('arango_compare.client.requests.get')
    def test_get_graphs(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'graphs': [{'name': 'graph1'}, {'name': 'graph2'}]}
        mock_get.return_value = mock_response

        client = ArangoDBClient('http://localhost:8529', 'root', 'password', 'test_db')
        graph_count = client.get_graphs()

        self.assertEqual(graph_count, 2)

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
        mock_response_graphs.json.return_value = {'graphs': [{'name': 'graph1'}, {'name': 'graph2'}]}

        mock_response_analyzers = Mock()
        mock_response_analyzers.json.return_value = {'result': [{'name': 'analyzer1'}, {'name': 'analyzer2'}]}

        mock_response_views = Mock()
        mock_response_views.json.return_value = {'result': [{'name': 'view1'}, {'name': 'view2'}]}

        mock_get.side_effect = [
            mock_response_collections, mock_response_doc_count, mock_response_indexes,
            mock_response_doc_count, mock_response_indexes, mock_response_graphs,
            mock_response_analyzers, mock_response_views
        ]

        client = ArangoDBClient('http://localhost:8529', 'root', 'password', 'test_db')
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
            'total_collections': 2,
            'total_documents': 200,
            'total_indexes': 4,
            'total_graphs': 2,
            'total_analyzers': 2,
            'total_views': 2,
            'collection_details': {
                'collection1': {'document_count': 100, 'index_count': 2},
                'collection2': {'document_count': 100, 'index_count': 2},
            }
        }

        summary2 = {
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
            }
        }

        compare_databases(summary1, summary2)

        print(mock_print_and_write.call_args_list)  # Debugging: Print all calls to print_and_write

        mock_print_and_write.assert_any_call("Summary of Differences".center(80), None)
        mock_print_and_write.assert_any_call("\nNumber of collections in DB1 not in DB2: 0", None)  # Updated line
        mock_print_and_write.assert_any_call("\nNumber of collections in DB2 not in DB1: 1", None)
        mock_print_and_write.assert_any_call("Collections unique to DB2:", None)
        mock_print_and_write.assert_any_call(" - collection3", None)
        mock_print_and_write.assert_any_call("\nNumber of collections with mismatched document or index counts: 0", None)

if __name__ == '__main__':
    unittest.main()

