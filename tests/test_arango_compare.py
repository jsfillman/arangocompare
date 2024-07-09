import unittest
from unittest import mock
from unittest.mock import patch, Mock, call
from arango_compare.client import ArangoDBClient
from arango_compare.comparator import compare_databases
import os
import tempfile
import datetime

class TestArangoDBClient(unittest.TestCase):

    @patch('arango_compare.client.requests.get')
    def test_get_collections(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {
            'result': [{'name': 'collection1'}, {'name': 'collection2'}],
            'hasMore': False
        }
        mock_get.return_value = mock_response

        client = ArangoDBClient('http://localhost:8529', 'root', 'password', 'test_db1')
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

        client = ArangoDBClient('http://localhost:8529', 'root', 'password', 'test_db1')
        details = client.get_collection_details('collection1')

        self.assertEqual(details['document_count'], 100)
        self.assertEqual(details['index_count'], 2)

    @patch('arango_compare.client.requests.get')
    def test_get_graphs(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = {'graphs': [{'name': 'graph1'}, {'name': 'graph2'}]}
        mock_get.return_value = mock_response

        client = ArangoDBClient('http://localhost:8529', 'root', 'password', 'test_db1')
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
            'views': [{'name': 'view1'}, {'name': 'view3'}]
        }

        with tempfile.TemporaryDirectory() as tmpdirname:
            client1 = Mock()  # Mock client1
            client2 = Mock()  # Mock client2
            compare_databases(client1, client2, summary1, summary2, tmpdirname)
            output_file = os.path.join(tmpdirname, f"test_db1-{datetime.datetime.now().strftime('%Y-%m-%d')}", "summary.md")

            # Check the calls to print_and_write
            calls = [
                call("# Document Checks", mock.ANY),
                call(f"\nComparing collections in database on servers **test_db1** and **test_db2**...\n", mock.ANY),
                call("# Summary of Differences", mock.ANY),
                call("\n**Number of collections in DB1 not in DB2:** 0", mock.ANY),
                call("\n**Number of collections in DB2 not in DB1:** 1", mock.ANY),
                call("### Collections unique to DB2:", mock.ANY),
                call("- collection3", mock.ANY),
                call("\n**Number of collections with mismatched document or index counts:** 0", mock.ANY),
                call("# Overall Feature Counts", mock.ANY),
                call(f"{'Feature':<30} {'DB1':>20} {'DB2':>20}", mock.ANY),
                call("-"*80, mock.ANY),
                call(f"{'Total collections':<30} {'2':>20} {'3':>20}", mock.ANY),
                call(f"{'Total documents':<30} {'200':>20} {'300':>20}", mock.ANY),
                call(f"{'Total indexes':<30} {'4':>20} {'6':>20}", mock.ANY),
                call(f"{'Total graphs':<30} {'2':>20} {'3':>20}", mock.ANY),
                call(f"{'Total analyzers':<30} {'2':>20} {'3':>20}", mock.ANY),
                call(f"{'Total views':<30} {'2':>20} {'3':>20}", mock.ANY)
            ]
            mock_print_and_write.assert_has_calls(calls, any_order=True)


if __name__ == '__main__':
    unittest.main()
