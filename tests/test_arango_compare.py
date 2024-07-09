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
            'total_collections': 3,  # Update to reflect collections unique to DB1
            'total_documents': 200,
            'total_indexes': 4,
            'total_graphs': 2,
            'total_analyzers': 2,
            'collection_details': {
                'collection1': {'document_count': 100, 'index_count': 2},
                'collection2': {'document_count': 100, 'index_count': 2},
                'collection4': {'document_count': 100, 'index_count': 2},  # Unique to DB1
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
                'collection3': {'document_count': 100, 'index_count': 2},  # Unique to DB2
            }
        }

        db_name1 = "test_db1"
        db_name2 = "test_db2"
        url1 = "http://localhost:8529"
        url2 = "http://localhost:8530"

        with tempfile.TemporaryDirectory() as tmpdirname:
            compare_databases(summary1, summary2, tmpdirname, db_name1, db_name2, url1, url2)

            # Check the calls to print_and_write
            calls = [
                call("# Comparing collections in database on servers\n", mock.ANY),
                call(f"\nComparing collections in {db_name1} on servers **{url1}** and **{url2}**...\n", mock.ANY),
                call("\n================================================================================", mock.ANY),
                call("\n                             Summary of Differences", mock.ANY),
                call("\n================================================================================\n", mock.ANY),
                call(f"Number of collections in DB1 not in DB2: {1}\n", mock.ANY),
                call(f"Number of collections in DB2 not in DB1: {1}\n", mock.ANY),
                call(f"Number of collections with mismatched document or index counts: {0}\n", mock.ANY),
                call("================================================================================", mock.ANY),
                call("\n                             Overall Feature Counts", mock.ANY),
                call("================================================================================", mock.ANY),
                call("Feature                                         DB1                  DB2", mock.ANY),
                call("--------------------------------------------------------------------------------", mock.ANY),
                call(f"Total collections                                {summary1['total_collections']}                   {summary2['total_collections']}", mock.ANY),
                call(f"Total documents                             {summary1['total_documents']}              {summary2['total_documents']}", mock.ANY),
                call(f"Total indexes                                    {summary1['total_indexes']}                   {summary2['total_indexes']}", mock.ANY),
                call(f"Total graphs                                      {summary1['total_graphs']}                    {summary2['total_graphs']}", mock.ANY),
                call(f"Total analyzers                                  {summary1['total_analyzers']}                   {summary2['total_analyzers']}", mock.ANY),
                call(f"Total views                                       {summary1.get('total_views', 0)}                    {summary2.get('total_views', 0)}", mock.ANY)
            ]
            mock_print_and_write.assert_has_calls(calls, any_order=True)
