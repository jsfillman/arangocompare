import unittest
from unittest.mock import patch, Mock
from arango_compare import ArangoDBClient, compare_databases

class TestArangoDBClient(unittest.TestCase):

    @patch('arango_compare.arango_compare.requests.get')
    def test_get_collections(self, mock_get):
        # Setup mock response
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

    @patch('arango_compare.arango_compare.requests.get')
    def test_get_collection_details(self, mock_get):
        # Setup mock response for document count
        mock_response_doc_count = Mock()
        mock_response_doc_count.json.return_value = {'count': 100}

        # Setup mock response for indexes
        mock_response_indexes = Mock()
        mock_response_indexes.json.return_value = {'indexes': [{'id': '1'}, {'id': '2'}]}

        mock_get.side_effect = [mock_response_doc_count, mock_response_indexes]

        client = ArangoDBClient('http://localhost:8529', 'root', 'password', 'test_db')
        details = client.get_collection_details('collection1')

        self.assertEqual(details['document_count'], 100)
        self.assertEqual(details['index_count'], 2)

    @patch('arango_compare.arango_compare.requests.get')
    def test_get_graphs(self, mock_get):
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {'graphs': [{'name': 'graph1'}, {'name': 'graph2'}]}
        mock_get.return_value = mock_response

        client = ArangoDBClient('http://localhost:8529', 'root', 'password', 'test_db')
        graph_count = client.get_graphs()

        self.assertEqual(graph_count, 2)

    @patch('arango_compare.arango_compare.requests.get')
    def test_get_analyzers(self, mock_get):
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {'result': [{'name': 'analyzer1'}, {'name': 'analyzer2'}]}
        mock_get.return_value = mock_response

        client = ArangoDBClient('http://localhost:8529', 'root', 'password', 'test_db')
        analyzers_count = client.get_analyzers()

        self.assertEqual(analyzers_count, 2)

    @patch('arango_compare.arango_compare.requests.get')
    def test_get_views(self, mock_get):
        # Setup mock response
        mock_response = Mock()
        mock_response.json.return_value = {'result': [{'name': 'view1'}, {'name': 'view2'}]}
        mock_get.return_value = mock_response

        client = ArangoDBClient('http://localhost:8529', 'root', 'password', 'test_db')
        views_count = client.get_views()

        self.assertEqual(views_count, 2)

    @patch('arango_compare.arango_compare.requests.get')
    def test_get_summary(self, mock_get):
        # Setup mock response for collections
        mock_response_collections = Mock()
        mock_response_collections.json.return_value = {
            'result': [{'name': 'collection1'}, {'name': 'collection2'}],
            'hasMore': False
        }

        # Setup mock response for document count and indexes
        mock_response_doc_count = Mock()
        mock_response_doc_count.json.return_value = {'count': 100}

        mock_response_indexes = Mock()
        mock_response_indexes.json.return_value = {'indexes': [{'id': '1'}, {'id': '2'}]}

        # Setup mock response for graphs
        mock_response_graphs = Mock()
        mock_response_graphs.json.return_value = {'graphs': [{'name': 'graph1'}, {'name': 'graph2'}]}

        # Setup mock response for analyzers
        mock_response_analyzers = Mock()
        mock_response_analyzers.json.return_value = {'result': [{'name': 'analyzer1'}, {'name': 'analyzer2'}]}

        # Setup mock response for views
        mock_response_views = Mock()
        mock_response_views.json.return_value = {'result': [{'name': 'view1'}, {'name': 'view2'}]}

        mock_get.side_effect = [mock_response_collections, mock_response_doc_count, mock_response_indexes,
                                mock_response_doc_count, mock_response_indexes, mock_response_graphs,
                                mock_response_analyzers, mock_response_views]

        client = ArangoDBClient('http://localhost:8529', 'root', 'password', 'test_db')
        summary = client.get_summary()

        self.assertEqual(summary['total_collections'], 2)
        self.assertEqual(summary['total_documents'], 200)
        self.assertEqual(summary['total_indexes'], 4)
        self.assertEqual(summary['total_graphs'], 2)
        self.assertEqual(summary['total_analyzers'], 2)
        self.assertEqual(summary['total_views'], 2)

    @patch('builtins.print')
    def test_compare_databases(self, mock_print):
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

        mock_print.assert_any_call("="*80)
        mock_print.assert_any_call("Summary of Differences".center(80))
        mock_print.assert_any_call("="*80)
        mock_print.assert_any_call("\nNumber of collections in DB1 not in DB2: 0")
        mock_print.assert_any_call("\nNumber of collections in DB2 not in DB1: 1")
        mock_print.assert_any_call("Collections unique to DB2:")
        mock_print.assert_any_call(" - collection3")
        mock_print.assert_any_call("\nNumber of collections with mismatched document or index counts: 0")
        mock_print.assert_any_call("\n" + "="*80)
        mock_print.assert_any_call("Overall Feature Counts".center(80))
        mock_print.assert_any_call("="*80)
        mock_print.assert_any_call(f"{'Feature':<30} {'DB1':>20} {'DB2':>20}")
        mock_print.assert_any_call("-"*80)
        mock_print.assert_any_call(f"{'Total collections':<30} {2:>20} {3:>20}")
        mock_print.assert_any_call(f"{'Total documents':<30} {200:>20} {300:>20}")
        mock_print.assert_any_call(f"{'Total indexes':<30} {4:>20} {6:>20}")
        mock_print.assert_any_call(f"{'Total graphs':<30} {2:>20} {3:>20}")
        mock_print.assert_any_call(f"{'Total analyzers':<30} {2:>20} {3:>20}")
        mock_print.assert_any_call(f"{'Total views':<30} {2:>20} {3:>20}")
        mock_print.assert_any_call("="*80)

if __name__ == '__main__':
    unittest.main()
