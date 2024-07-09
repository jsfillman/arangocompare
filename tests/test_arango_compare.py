from unittest import TestCase, mock
from unittest.mock import patch, call
import tempfile
from arango_compare.comparator import compare_databases

class TestArangoDBClient(TestCase):

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

            # Print actual calls for debugging
            print("Actual calls to print_and_write:")
            for call in mock_print_and_write.mock_calls:
                print(call)

            # Check the calls to print_and_write for collections.md
            collections_calls = [
                call("# Collections Comparison", mock.ANY),
                call(f"\nComparing collections in {db_name1} on servers **{url1}** and **{url2}**...\n", mock.ANY),
                call("\n## Collection: collection1\n", mock.ANY),
                call("| Property | test_db1 | test_db2 |\n", mock.ANY),
                call("|----------|-------------|-------------|\n", mock.ANY),
                call("| Document count | 100 | 100 |\n", mock.ANY),
                call("| Index count | 2 | 2 |\n", mock.ANY),
                call("\n## Collection: collection2\n", mock.ANY),
                call("| Property | test_db1 | test_db2 |\n", mock.ANY),
                call("|----------|-------------|-------------|\n", mock.ANY),
                call("| Document count | 100 | 100 |\n", mock.ANY),
                call("| Index count | 2 | 2 |\n", mock.ANY),
                call("\n## Collection: collection4\n", mock.ANY),
                call("| Property | test_db1 | test_db2 |\n", mock.ANY),
                call("|----------|-------------|-------------|\n", mock.ANY),
                call("| Document count | 100 | 0 |\n", mock.ANY),
                call("| Index count | 2 | 0 |\n", mock.ANY),
                call("\n## Collection: collection3\n", mock.ANY),
                call("| Property | test_db1 | test_db2 |\n", mock.ANY),
                call("|----------|-------------|-------------|\n", mock.ANY),
                call("| Document count | 0 | 100 |\n", mock.ANY),
                call("| Index count | 0 | 2 |\n", mock.ANY),
            ]

            # Check the calls to print_and_write for summary.md
            summary_calls = [
                call("================================================================================", mock.ANY),
                call("\n                             Summary of Differences\n", mock.ANY),
                call("================================================================================", mock.ANY),
                call(f"\nNumber of collections in DB1 not in DB2: {1}\n", mock.ANY),
                call(f"Number of collections in DB2 not in DB1: {1}\n", mock.ANY),
                call(f"Number of collections with mismatched document or index counts: {0}\n", mock.ANY),
                call("================================================================================", mock.ANY),
                call("\n                             Overall Feature Counts\n", mock.ANY),
                call("================================================================================", mock.ANY),
                call("Feature                                         DB1                  DB2\n", mock.ANY),
                call("--------------------------------------------------------------------------------", mock.ANY),
                call(f"Total collections                                {summary1['total_collections']}                   {summary2['total_collections']}\n", mock.ANY),
                call(f"Total documents                             {summary1['total_documents']}              {summary2['total_documents']}\n", mock.ANY),
                call(f"Total indexes                                    {summary1['total_indexes']}                   {summary2['total_indexes']}\n", mock.ANY),
                call(f"Total graphs                                      {summary1['total_graphs']}                    {summary2['total_graphs']}\n", mock.ANY),
                call(f"Total analyzers                                  {summary1['total_analyzers']}                   {summary2['total_analyzers']}\n", mock.ANY),
                call(f"Total views                                       {summary1.get('total_views', 0)}                    {summary2.get('total_views', 0)}\n", mock.ANY)
            ]

            # Assert each call in collections_calls and summary_calls
            for expected_call in collections_calls + summary_calls:
                if expected_call not in mock_print_and_write.mock_calls:
                    print(f"Missing call: {expected_call}")

            mock_print_and_write.assert_has_calls(collections_calls, any_order=True)
            mock_print_and_write.assert_has_calls(summary_calls, any_order=True)
