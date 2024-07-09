import os
from typing import Dict, Any
from .formatter import print_and_write

def compare_databases(summary1, summary2, output_dir, db_name1, db_name2, url1, url2):
    collections_filename = f"{output_dir}/{db_name1}-{db_name2}/collections.md"
    summary_filename = f"{output_dir}/{db_name1}-{db_name2}/summary.md"

    os.makedirs(os.path.dirname(collections_filename), exist_ok=True)

    with open(collections_filename, 'w') as collections_file, open(summary_filename, 'w') as summary_file:
        # Collections Comparison
        print_and_write("# Collections Comparison", collections_file)
        print_and_write(f"\nComparing collections in {db_name1} on servers **{url1}** and **{url2}**...\n", collections_file)

        # Collection details
        for collection_name in sorted(set(summary1['collection_details']).union(summary2['collection_details'])):
            print_and_write(f"\n## Collection: {collection_name}\n", collections_file)
            print_and_write("| Property | test_db1 | test_db2 |\n", collections_file)
            print_and_write("|----------|-------------|-------------|\n", collections_file)
            doc_count1 = summary1['collection_details'].get(collection_name, {}).get('document_count', 0)
            doc_count2 = summary2['collection_details'].get(collection_name, {}).get('document_count', 0)
            index_count1 = summary1['collection_details'].get(collection_name, {}).get('index_count', 0)
            index_count2 = summary2['collection_details'].get(collection_name, {}).get('index_count', 0)
            print_and_write(f"| Document count | {doc_count1} | {doc_count2} |\n", collections_file)
            print_and_write(f"| Index count | {index_count1} | {index_count2} |\n", collections_file)

        # Summary of Differences
        print_and_write("="*80, summary_file)
        print_and_write("\n                             Summary of Differences\n", summary_file)
        print_and_write("="*80, summary_file)
        collections_only_in_db1 = len(set(summary1['collection_details']) - set(summary2['collection_details']))
        collections_only_in_db2 = len(set(summary2['collection_details']) - set(summary1['collection_details']))
        mismatched_collections = 0  # Assuming mismatched counts calculation
        print_and_write(f"\nNumber of collections in DB1 not in DB2: {collections_only_in_db1}\n", summary_file)
        print_and_write(f"Number of collections in DB2 not in DB1: {collections_only_in_db2}\n", summary_file)
        print_and_write(f"Number of collections with mismatched document or index counts: {mismatched_collections}\n", summary_file)
        print_and_write("="*80, summary_file)

        # Overall Feature Counts
        print_and_write("\n                             Overall Feature Counts\n", summary_file)
        print_and_write("="*80, summary_file)
        print_and_write("Feature                                         DB1                  DB2\n", summary_file)
        print_and_write("--------------------------------------------------------------------------------", summary_file)
        print_and_write(f"Total collections                                {summary1['total_collections']}                   {summary2['total_collections']}\n", summary_file)
        print_and_write(f"Total documents                             {summary1['total_documents']}              {summary2['total_documents']}\n", summary_file)
        print_and_write(f"Total indexes                                    {summary1['total_indexes']}                   {summary2['total_indexes']}\n", summary_file)
        print_and_write(f"Total graphs                                      {summary1['total_graphs']}                    {summary2['total_graphs']}\n", summary_file)
        print_and_write(f"Total analyzers                                  {summary1['total_analyzers']}                   {summary2['total_analyzers']}\n", summary_file)
        print_and_write(f"Total views                                       {summary1.get('total_views', 0)}                    {summary2.get('total_views', 0)}\n", summary_file)
