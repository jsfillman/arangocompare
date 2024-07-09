import os
import datetime
from typing import Dict, Any
from .formatter import print_and_write

def compare_databases(summary1, summary2, output_dir, db_name1, db_name2, url1, url2):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
    output_dir = os.path.join(output_dir, f"{db_name1}-{timestamp}")
    collections_filename = os.path.join(output_dir, 'collections.md')
    summary_filename = os.path.join(output_dir, 'summary.md')
    analyzers_filename = os.path.join(output_dir, 'analyzers.md')

    os.makedirs(os.path.dirname(collections_filename), exist_ok=True)

    with open(collections_filename, 'w') as collections_file, open(summary_filename, 'w') as summary_file, open(analyzers_filename, 'w') as analyzers_file:
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
        collections_only_in_db1 = set(summary1['collection_details']) - set(summary2['collection_details'])
        collections_only_in_db2 = set(summary2['collection_details']) - set(summary1['collection_details'])
        mismatched_collections = set(collection_name for collection_name in summary1['collection_details']
                                     if collection_name in summary2['collection_details']
                                     and (summary1['collection_details'][collection_name]['document_count'] != summary2['collection_details'][collection_name]['document_count']
                                          or summary1['collection_details'][collection_name]['index_count'] != summary2['collection_details'][collection_name]['index_count']))

        print_and_write(f"\nNumber of collections in DB1 not in DB2: {len(collections_only_in_db1)}\n", summary_file)
        if collections_only_in_db1:
            print_and_write(f"Names: {', '.join(collections_only_in_db1)}\n", summary_file)

        print_and_write(f"\nNumber of collections in DB2 not in DB1: {len(collections_only_in_db2)}\n", summary_file)
        if collections_only_in_db2:
            print_and_write(f"Names: {', '.join(collections_only_in_db2)}\n", summary_file)

        print_and_write(f"\nNumber of collections with mismatched document or index counts: {len(mismatched_collections)}\n", summary_file)
        if mismatched_collections:
            print_and_write(f"Names: {', '.join(mismatched_collections)}\n", summary_file)

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

        # Analyzers Comparison
        if 'analyzers' in summary1 or 'analyzers' in summary2:
            print_and_write("# Analyzer Differences", analyzers_file)
            analyzers1 = summary1.get('analyzers', {})
            analyzers2 = summary2.get('analyzers', {})
            for analyzer_name in sorted(set(analyzers1).union(analyzers2)):
                print_and_write(f"\n## Analyzer: {analyzer_name}\n", analyzers_file)
                print_and_write("- **properties**:\n", analyzers_file)
                properties1 = analyzers1.get(analyzer_name, {}).get('properties', {})
                properties2 = analyzers2.get(analyzer_name, {}).get('properties', {})
                print_and_write(f"  - DB1: {properties1}\n", analyzers_file)
                print_and_write(f"  - DB2: {properties2}\n", analyzers_file)
                print_and_write("- **features**:\n", analyzers_file)
                features1 = analyzers1.get(analyzer_name, {}).get('features', [])
                features2 = analyzers2.get(analyzer_name, {}).get('features', [])
                print_and_write(f"  - DB1: {features1}\n", analyzers_file)
                print_and_write(f"  - DB2: {features2}\n", analyzers_file)

            # Analyze unique analyzers
            analyzers_only_in_db1 = set(analyzers1) - set(analyzers2)
            analyzers_only_in_db2 = set(analyzers2) - set(analyzers1)
            for analyzer_name in analyzers_only_in_db1:
                print_and_write(f"\n## Analyzer only in DB1: {analyzer_name}\n", analyzers_file)
            for analyzer_name in analyzers_only_in_db2:
                print_and_write(f"\n## Analyzer only in DB2: {analyzer_name}\n", analyzers_file)
