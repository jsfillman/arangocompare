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
    output_file = os.path.join(log_subdir, "summary.md")

    output = open(output_file, 'w') if output_file else None

    print_and_write("# Document Checks", output)
    print_and_write(f"\nComparing collections in database on servers **{summary1['db_name']}** and **{summary2['db_name']}**...\n", output)

    for collection in matching_collections:
        details1 = summary1['collection_details'][collection]
        details2 = summary2['collection_details'][collection]
        if details1['document_count'] != details2['document_count'] or details1['index_count'] != details2['index_count']:
            mismatched_collections.append(collection)
            print_and_write(f"\nCollection name: {collection}", output)
            print_and_write(f"  Server1 - Document count: {details1['document_count']}, Index count: {details1['index_count']}", output)
            print_and_write(f"  Server2 - Document count: {details2['document_count']}, Index count: {details2['index_count']}", output)

    print_and_write("# Summary of Differences", output)

    print_and_write(f"\n**Number of collections in DB1 not in DB2:** {len(unique_to_db1)}", output)
    if unique_to_db1:
        print_and_write("### Collections unique to DB1:", output)
        for collection in unique_to_db1:
            print_and_write(f"- {collection}", output)

    print_and_write(f"\n**Number of collections in DB2 not in DB1:** {len(unique_to_db2)}", output)
    if unique_to_db2:
        print_and_write("### Collections unique to DB2:", output)
        for collection in unique_to_db2:
            print_and_write(f"- {collection}", output)

    print_and_write(f"\n**Number of collections with mismatched document or index counts:** {len(mismatched_collections)}", output)
    if mismatched_collections:
        print_and_write("### Collections with mismatched counts:", output)
        for collection in mismatched_collections:
            print_and_write(f"- {collection}", output)

    print_and_write("# Overall Feature Counts", output)
    print_and_write(f"{'Feature':<30} {'DB1':>20} {'DB2':>20}", output)
    print_and_write("-"*80, output)
    print_and_write(f"{'Total collections':<30} {summary1['total_collections']:>20} {summary2['total_collections']:>20}", output)
    print_and_write(f"{'Total documents':<30} {summary1['total_documents']:>20} {summary2['total_documents']:>20}", output)
    print_and_write(f"{'Total indexes':<30} {summary1['total_indexes']:>20} {summary2['total_indexes']:>20}", output)
    print_and_write(f"{'Total graphs':<30} {summary1['total_graphs']:>20} {summary2['total_graphs']:>20}", output)
    print_and_write(f"{'Total analyzers':<30} {summary1['total_analyzers']:>20} {summary2['total_analyzers']:>20}", output)
    print_and_write(f"{'Total views':<30} {summary1['total_views']:>20} {summary2['total_views']:>20}", output)

    if output:
        output.close()
