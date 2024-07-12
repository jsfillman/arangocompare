import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import json

# Adjust the path to include the parent directory where the modules are located
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'arango_compare')))

from client import ArangoDBClient
from formatter import Formatter
from comparator import Comparator
from main import write_discrepancies_to_md

class TestArangoCompare(unittest.TestCase):

    @patch('client.requests.get')
    def test_get_all_entities(self, mock_get):
        # Mocking collection and index responses
        mock_collections_response = MagicMock()
        mock_collections_response.json.return_value = {
            'result': [{'name': 'collection1', 'count': 1, 'status': 'loaded'}]
        }
        mock_indexes_response = MagicMock()
        mock_indexes_response.json.return_value = {
            'indexes': [{'id': 'index1', 'type': 'hash', 'fields': ['field1'], 'unique': True, 'sparse': False}]
        }

        mock_get.side_effect = [mock_collections_response, mock_indexes_response]

        client = ArangoDBClient('http://example.com', 'test_db')
        entities = client.get_all_entities()

        expected_entities = {
            'collections': [{'name': 'collection1', 'count': 1, 'status': 'loaded'}],
            'indexes': {
                'collection1': [{'id': 'index1', 'type': 'hash', 'fields': ['field1'], 'unique': True, 'sparse': False}]
            }
        }

        self.assertEqual(entities, expected_entities)

    def test_format_entities(self):
        formatter = Formatter()
        entities = {
            'collections': [{'name': 'collection1', 'count': 1, 'status': 'loaded'}],
            'indexes': {
                'collection1': [{'id': 'index1', 'type': 'hash', 'fields': ['field1'], 'unique': True, 'sparse': False}]
            }
        }

        formatted_entities = formatter.format_entities(entities)
        expected_formatted_entities = {
            'collections': {
                'collection1': {'count': 1, 'status': 'loaded'}
            },
            'indexes': {
                'collection1': {
                    'index1': {'type': 'hash', 'fields': ['field1'], 'unique': True, 'sparse': False}
                }
            }
        }

        self.assertEqual(formatted_entities, expected_formatted_entities)

    def test_compare_entities(self):
        comparator = Comparator()
        source_entities = {
            'collections': {
                'collection1': {'count': 1, 'status': 'loaded'}
            },
            'indexes': {
                'collection1': {
                    'index1': {'type': 'hash', 'fields': ['field1'], 'unique': True, 'sparse': False}
                }
            }
        }
        target_entities = {
            'collections': {
                'collection1': {'count': 1, 'status': 'unloaded'}
            },
            'indexes': {
                'collection1': {
                    'index1': {'type': 'hash', 'fields': ['field1'], 'unique': False, 'sparse': False}
                }
            }
        }

        discrepancies = comparator.compare_entities(source_entities, target_entities)
        expected_discrepancies = {
            'collections': {
                'collection1': {
                    'source': {'count': 1, 'status': 'loaded'},
                    'target': {'count': 1, 'status': 'unloaded'}
                }
            },
            'indexes': {
                'collection1': {
                    'index1': {
                        'source': {'type': 'hash', 'fields': ['field1'], 'unique': True, 'sparse': False},
                        'target': {'type': 'hash', 'fields': ['field1'], 'unique': False, 'sparse': False}
                    }
                }
            }
        }

        self.assertEqual(discrepancies, expected_discrepancies)

    def test_write_discrepancies_to_md(self):
        discrepancies = {
            'collections': {
                'collection1': {
                    'source': {'count': 1, 'status': 'loaded'},
                    'target': {'count': 1, 'status': 'unloaded'}
                }
            },
            'indexes': {
                'collection1': {
                    'index1': {
                        'source': {'type': 'hash', 'fields': ['field1'], 'unique': True, 'sparse': False},
                        'target': {'type': 'hash', 'fields': ['field1'], 'unique': False, 'sparse': False}
                    }
                }
            }
        }

        output_dir = 'test_output'
        write_discrepancies_to_md(discrepancies, output_dir)

        collections_md_path = os.path.join(output_dir, "collection_discrepancies.md")
        indexes_md_path = os.path.join(output_dir, "index_discrepancies.md")

        with open(collections_md_path, 'r') as collections_md_file:
            collections_content = collections_md_file.read()
            self.assertIn("Collection Discrepancies", collections_content)
            self.assertIn(json.dumps(discrepancies['collections'], indent=2), collections_content)

        with open(indexes_md_path, 'r') as indexes_md_file:
            indexes_content = indexes_md_file.read()
            self.assertIn("Index Discrepancies", indexes_content)
            self.assertIn(json.dumps(discrepancies['indexes'], indent=2), indexes_content)

        # Clean up
        os.remove(collections_md_path)
        os.remove(indexes_md_path)
        os.rmdir(output_dir)

if __name__ == '__main__':
    unittest.main()
