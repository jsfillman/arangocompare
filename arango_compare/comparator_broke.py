import os
import datetime
from typing import Dict, Any
from .formatter import print_and_write

def compare_analyzer_details(client1, client2, analyzers1: Dict[str, Any], analyzers2: Dict[str, Any], log_subdir: str) -> None:
    analyzer_diffs = []
    analyzers_file = os.path.join(log_subdir, "analyzers.md")
    analyzers_output = open(analyzers_file, 'w') if analyzers_file else None

    print_and_write("# Analyzer Differences", analyzers_output)

    analyzers1_names = {analyzer['name'] for analyzer in analyzers1}
    analyzers2_names = {analyzer['name'] for analyzer in analyzers2}

    unique_to_db1 = analyzers1_names - analyzers2_names
    unique_to_db2 = analyzers2_names - analyzers1_names
    matching_analyzers = analyzers1_names & analyzers2_names

    for analyzer in unique_to_db1:
        print_and_write(f"\n## Analyzer only in DB1: {analyzer}", analyzers_output)

    for analyzer in unique_to_db2:
        print_and_write(f"\n## Analyzer only in DB2: {analyzer}", analyzers_output)

    for analyzer in matching_analyzers:
        details1 = client1.get_analyzer_details(analyzer)
        details2 = client2.get_analyzer_details(analyzer)
        if details1 != details2:
            print_and_write(f"\n## Analyzer: {analyzer}", analyzers_output)
            print_and_write(f"### Server1 details:\n{details1}", analyzers_output)
            print_and_write(f"### Server2 details:\n{details2}", analyzers_output)

    if analyzers_output:
        analyzers_output.close()

def compare_databases(client1, client2, summary1: Dict[str, Any], summary2: Dict[str, Any], log_dir: str) -> None:
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
    summary_file = os.path.join(log_subdir, "summary.md")
    collections_file = os.path.join(log_subdir, "collections.md")

    summary_output = open(summary_file, 'w') if summary_file else None
    collections_output = open(collections_file, 'w') if collections_file else None

    print_and_write("# Summary", summary_output)
    print_and_write("\nPerforming document/index checks...", summary_output)

    for collection in matching_collections:
        details1 = summary1['collection_details'][collection]
        details2 = summary2['collection_details'][collection]
        if details1['document_count'] != details2['document_count'] or details1['index_count'] != details2['index_count']:
            mismatched_collections.append(collection)
            print_and_write(f"\nCollection name: {collection}", collections_output)
            print_and_write(f"  Server1 - Document count: {details1['document_count']}, Index count: {details1['index_count']}", collections_output)
            print_and_write(f"  Server2 - Document count: {details2['document_count']}, Index count: {details2['index_count']}", collections_output)

    print_and_write("\nDocument/index checks completed.", summary_output)
    print_and_write("Performing analyzer comparisons...", summary_output)

    compare_analyzer_details(client1, client2, summary1['analyzers'], summary2['analyzers'], log_subdir)

    print_and_write("Analyzer comparisons completed.", summary_output)

    print_and_write("# Summary of Differences", summary_output)

    print_and_write(f"\n**Number of collections in DB1 not in DB2:** {len(unique_to_db1)}", summary_output)
    if unique_to_db1:
        print_and_write("### Collections unique to DB1:", summary_output)
        for collection in unique_to_db1:
            print_and_write(f"- {collection}", summary_output)

    print_and_write(f"\n**Number of collections in DB2 not in DB1:** {len(unique_to_db2)}", summary_output)
    if unique_to_db2:
        print_and_write("### Collections unique to DB2:", summary_output)
        for collection in unique_to_db2:
            print_and_write(f"- {collection}", summary_output)

    print_and_write(f"\n**Number of collections with mismatched document or index counts:** {len(mismatched_collections)}", summary_output)
    if mismatched_collections:
        print_and_write("### Collections with mismatched counts:", summary_output)
        for collection in mismatched_collections:
            print_and_write(f"- {collection}", summary_output)

    print_and_write("# Overall Feature Counts", summary_output)
    print_and_write(f"{'Feature':<30} {'DB1':>20} {'DB2':>20}", summary_output)
    print_and_write("-"*80, summary_output)
    print_and_write(f"{'Total collections':<30} {summary1['total_collections']:>20} {summary2['total_collections']:>20}", summary_output)
    print_and_write(f"{'Total documents':<30} {summary1['total_documents']:>20} {summary2['total_documents']:>20}", summary_output)
    print_and_write(f"{'Total indexes':<30} {summary1['total_indexes']:>20} {summary2['total_indexes']:>20}", summary_output)
    print_and_write(f"{'Total graphs':<30} {summary1['total_graphs']:>20} {summary2['total_graphs']:>20}", summary_output)
    print_and_write(f"{'Total analyzers':<30} {summary1['total_analyzers']:>20} {summary2['total_analyzers']:>20}", summary_output)
    print_and_write(f"{'Total views':<30} {summary1['total_views']:>20} {summary2['total_views']:>20}", summary_output)

    if summary_output:
        summary_output.close()
    if collections_output:
        collections_output.close()
