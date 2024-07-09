import os
import datetime
from typing import Dict, Any
from .formatter import print_and_write

def compare_databases(summary1: Dict[str, Any], summary2: Dict[str, Any], log_dir: str) -> None:
    collections1 = set(summary1['collection_details'].keys())
    collections2 = set(summary2['collection_details'].keys())

    unique_to_db1 = collections1 - collections2
    unique_to_db2 = collections2 - collections1
    matching_collections = collections1 & collections2

    mismatched_collections = []

    db_name = summary1['db_name']
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    log_subdir = os.path.join(log_dir, f"{db_name}-{date_str}")
    os.makedirs(log_subdir, exist_ok=True)

    collections_file = os.path.join(log_subdir, "collections.md")
    summary_file = os.path.join(log_subdir, "summary.md")

    collections_output = open(collections_file, 'w')
    summary_output = open(summary_file, 'w')

    print_and_write("# Comparing collections in database on servers\n", summary_output)
    print_and_write(f"\nComparing collections in database on servers **{summary1['db_name']}** and **{summary2['db_name']}**...\n", collections_output)

    for collection in matching_collections:
        details1 = summary1['collection_details'][collection]
        details2 = summary2['collection_details'][collection]
        if details1['document_count'] != details2['document_count'] or details1['index_count'] != details2['index_count']:
            mismatched_collections.append(collection)
            print_and_write(f"\nCollection name: {collection}", collections_output)
            print_and_write(f"  Server1 - Document count: {details1['document_count']}, Index count: {details1['index_count']}", collections_output)
            print_and_write(f"  Server2 - Document count: {details2['document_count']}, Index count: {details2['index_count']}", collections_output)

    print_and_write("\n\n================================================================================", summary_output)
    print_and_write("\n                             Summary of Differences", summary_output)
    print_and_write("\n================================================================================\n", summary_output)

    print_and_write(f"\nNumber of collections in DB1 not in DB2: {len(unique_to_db1)}\n", summary_output)
    print_and_write(f"Number of collections in DB2 not in DB1: {len(unique_to_db2)}\n", summary_output)
    print_and_write(f"Number of collections with mismatched document or index counts: {len(mismatched_collections)}\n", summary_output)

    if mismatched_collections:
        print_and_write("### Collections with mismatched counts:\n", summary_output)
        for collection in mismatched_collections:
            print_and_write(f" {collection}", summary_output)

    print_and_write("\n\n================================================================================", summary_output)
    print_and_write("\n                             Overall Feature Counts", summary_output)
    print_and_write("\n================================================================================", summary_output)

    print_and_write(f"\nFeature                                         DB1                  DB2\n", summary_output)
    print_and_write(f"--------------------------------------------------------------------------------\n", summary_output)
    print_and_write(f"Total collections                                {summary1['total_collections']}                   {summary2['total_collections']}\n", summary_output)
    print_and_write(f"Total documents                             {summary1['total_documents']}              {summary2['total_documents']}\n", summary_output)
    print_and_write(f"Total indexes                                    {summary1['total_indexes']}                   {summary2['total_indexes']}\n", summary_output)
    print_and_write(f"Total graphs                                      {summary1['total_graphs']}                    {summary2['total_graphs']}\n", summary_output)
    print_and_write(f"Total analyzers                                  {summary1['total_analyzers']}                   {summary2['total_analyzers']}\n", summary_output)
    print_and_write(f"Total views                                       {summary1.get('total_views', 0)}                    {summary2.get('total_views', 0)}\n", summary_output)

    collections_output.close()
    summary_output.close()

