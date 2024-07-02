import unittest
from unittest.mock import patch, Mock
from arango_compare import ArangoDBClient

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

        mock_get.side_effect = [mock_response_collections, mock_response_doc_count, mock_response_indexes,
                                mock_response_doc_count, mock_response_indexes, mock_response_graphs]

        client = ArangoDBClient('http://localhost:8529', 'root', 'password', 'test_db')
        summary = client.get_summary()

        self.assertEqual(summary['total_collections'], 2)
        self.assertEqual(summary['total_documents'], 200)
        self.assertEqual(summary['total_indexes'], 4)
        self.assertEqual(summary['total_graphs'], 2)

if __name__ == '__main__':
    unittest.main()
