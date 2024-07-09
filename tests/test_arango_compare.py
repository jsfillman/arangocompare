from unittest import TestCase, mock
from unittest.mock import patch, Mock, call
import tempfile
import os
import datetime
from arango_compare.client import ArangoDBClient
from arango_compare.comparator import compare_databases

class TestArangoDBClient(TestCase):

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

    @patch('arango_compare.comparator.print_and_write')
    def test_compare_databases(self, mock_print_and_write):
        summary1 = {
            'db_name': 'test_db1',
            'total_collections': 2,
            'total_documents': 200,
            'total_indexes': 4,
            'total_graphs': 2,
            'total_analyzers': 2,
            'collection_details': {
                'collection1': {'document_count': 100, 'index_count': 2},
                'collection2': {'document_count': 100, 'index_count': 2},
            }
        }

        summary2 = {
            'db_name': 'test_db2',
            'total_collections': 3,
            'total_documents': 300,
            'total_indexes': 6,
            'total_graphs': 3,
            'total_analyzers': 3,
            'collection_details': {
                'collection1': {'document_count': 100, 'index_count': 2},
                'collection2': {'document_count': 100, 'index_count': 2},
                'collection3': {'document_count': 100, 'index_count': 2},
            }
        }

        with tempfile.TemporaryDirectory() as tmpdirname:
            compare_databases(summary1, summary2, tmpdirname)

            # Check the calls to print_and_write
            calls = [
                call("# Comparing collections in database on servers\n", mock.ANY),
                call("\n\n================================================================================", mock.ANY),
                call("\n                             Summary of Differences", mock.ANY),
                call("\n================================================================================\n", mock.ANY),
                call("\nNumber of collections in DB1 not in DB2: 0\n", mock.ANY),
                call("Number of collections in DB2 not in DB1: 1\n", mock.ANY),
                call("Number of collections with mismatched document or index counts: 0\n", mock.ANY),
                call("\n\n================================================================================", mock.ANY),
                call("\n                             Overall Feature Counts", mock.ANY),
                call("\n================================================================================", mock.ANY),
                call("\nFeature                                         DB1                  DB2\n", mock.ANY),
                call("--------------------------------------------------------------------------------\n", mock.ANY),
                call("Total collections                                2                   3\n", mock.ANY),
                call("Total documents                             200              300\n", mock.ANY),
                call("Total indexes                                    4                   6\n", mock.ANY),
                call("Total graphs                                      2                    3\n", mock.ANY),
                call("Total analyzers                                  2                   3\n", mock.ANY),
                call("Total views                                       0                    0\n", mock.ANY),
            ]
            mock_print_and_write.assert_has_calls(calls, any_order=True)

            