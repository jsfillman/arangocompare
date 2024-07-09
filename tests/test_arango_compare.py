import unittest
from unittest.mock import patch, call, ANY
import tempfile
import os
from arango_compare.comparator import compare_databases

class TestArangoDBClient(unittest.TestCase):

    @patch('arango_compare.comparator.print_and_write')
    def test_compare_databases(self, mock_print_and_write):
        summary1 = {
            'db_name': 'test_db1',
            'total_collections': 3,
            'total_documents': 200,
            'total_indexes': 4,
            'total_graphs': 2,
            'total_analyzers': 2,
            'collection_details': {
                'collection1': {'document_count': 100, 'index_count': 2},
                'collection2': {'document_count': 100, 'index_count': 2},
                'collection4': {'document_count': 100, 'index_count': 2},
            },
            'analyzers': {
                'text_sv': {'properties': {'locale': 'sv.utf-8', 'case': 'lower', 'stopwords': [], 'accent': False, 'stemming': True}, 'features': ['position', 'norm', 'frequency']}
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
            },
            'analyzers': {
                'text_sv': {'properties': {'locale': 'sv', 'case': 'lower', 'stopwords': [], 'accent': False, 'stemming': True}, 'features': ['frequency', 'position', 'norm']},
                'text_nl': {'properties': {'locale': 'nl.utf-8', 'case': 'lower', 'stopwords': [], 'accent': False, 'stemming': True}, 'features': ['position', 'norm', 'frequency']}
            }
        }

        db_name1 = "test_db1"
        db_name2 = "test_db2"
        url1 = "http://localhost:8529"
        url2 = "http://localhost:8530"

        with tempfile.TemporaryDirectory() as tmpdirname:
            compare_databases(summary1, summary2, tmpdirname, db_name1, db_name2, url1, url2)

            # Verify directory and file creation
            created_dir = os.listdir(tmpdirname)[0]
            self.assertTrue(created_dir.startswith(db_name1))
            created_path = os.path.join(tmpdirname, created_dir)
            self.assertTrue(os.path.isdir(created_path))
            self.assertTrue(os.path.isfile(os.path.join(created_path, 'collections.md')))
            self.assertTrue(os.path.isfile(os.path.join(created_path, 'summary.md')))
            self.assertTrue(os.path.isfile(os.path.join(created_path, 'analyzers.md')))

            # Verify calls to print_and_write for collections.md
            collections_calls = [
                call("# Collections Comparison", ANY),
                call(f"\nComparing collections in {db_name1} on servers **{url1}** and **{url2}**...\n", ANY),
                call("\n## Collection: collection1\n", ANY),
                call("| Property | test_db1 | test_db2 |\n", ANY),
                call("|----------|-------------|-------------|\n", ANY),
                call("| Document count | 100 | 100 |\n", ANY),
                call("| Index count | 2 | 2 |\n", ANY),
                call("\n## Collection: collection2\n", ANY),
                call("| Property | test_db1 | test_db2 |\n", ANY),
                call("|----------|-------------|-------------|\n", ANY),
                call("| Document count | 100 | 100 |\n", ANY),
                call("| Index count | 2 | 2 |\n", ANY),
                call("\n## Collection: collection3\n", ANY),
                call("| Property | test_db1 | test_db2 |\n", ANY),
                call("|----------|-------------|-------------|\n", ANY),
                call("| Document count | 0 | 100 |\n", ANY),
                call("| Index count | 0 | 2 |\n", ANY),
                call("\n## Collection: collection4\n", ANY),
                call("| Property | test_db1 | test_db2 |\n", ANY),
                call("|----------|-------------|-------------|\n", ANY),
                call("| Document count | 100 | 0 |\n", ANY),
                call("| Index count | 2 | 0 |\n", ANY),
            ]
            mock_print_and_write.assert_has_calls(collections_calls, any_order=True)

            # Verify calls to print_and_write for summary.md
            summary_calls = [
                call("="*80, ANY),
                call("\n                             Summary of Differences\n", ANY),
                call("="*80, ANY),
                call(f"\nNumber of collections in DB1 not in DB2: 1\n", ANY),
                call("Names: collection4\n", ANY),
                call(f"\nNumber of collections in DB2 not in DB1: 1\n", ANY),
                call("Names: collection3\n", ANY),
                call(f"\nNumber of collections with mismatched document or index counts: 0\n", ANY),
                call("="*80, ANY),
                call("\n                             Overall Feature Counts\n", ANY),
                call("="*80, ANY),
                call("Feature                                         DB1                  DB2\n", ANY),
                call("--------------------------------------------------------------------------------", ANY),
                call(f"Total collections                                {summary1['total_collections']}                   {summary2['total_collections']}\n", ANY),
                call(f"Total documents                             {summary1['total_documents']}              {summary2['total_documents']}\n", ANY),
                call(f"Total indexes                                    {summary1['total_indexes']}                   {summary2['total_indexes']}\n", ANY),
                call(f"Total graphs                                      {summary1['total_graphs']}                    {summary2['total_graphs']}\n", ANY),
                call(f"Total analyzers                                  {summary1['total_analyzers']}                   {summary2['total_analyzers']}\n", ANY),
                call(f"Total views                                       {summary1.get('total_views', 0)}                    {summary2.get('total_views', 0)}\n", ANY),
            ]
            mock_print_and_write.assert_has_calls(summary_calls, any_order=True)

            # Verify calls to print_and_write for analyzers.md
            analyzers_calls = [
                call("# Analyzer Differences", ANY),
                call("\n## Analyzer: text_sv\n", ANY),
                call("- **properties**:\n", ANY),
                call(f"  - DB1: {summary1['analyzers']['text_sv']['properties']}\n", ANY),
                call(f"  - DB2: {summary2['analyzers']['text_sv']['properties']}\n", ANY),
                call("- **features**:\n", ANY),
                call(f"  - DB1: {summary1['analyzers']['text_sv']['features']}\n", ANY),
                call(f"  - DB2: {summary2['analyzers']['text_sv']['features']}\n", ANY),
                call("\n## Analyzer: text_nl\n", ANY),
                call("- **properties**:\n", ANY),
                call(f"  - DB1: {{}}\n", ANY),
                call(f"  - DB2: {summary2['analyzers']['text_nl']['properties']}\n", ANY),
                call("- **features**:\n", ANY),
                call(f"  - DB1: []\n", ANY),
                call(f"  - DB2: {summary2['analyzers']['text_nl']['features']}\n", ANY),
                call("\n## Analyzer only in DB2: text_nl\n", ANY)
            ]
            mock_print_and_write.assert_has_calls(analyzers_calls, any_order=True)

if __name__ == '__main__':
    unittest.main()
