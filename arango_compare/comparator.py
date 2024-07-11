import os
import datetime
from typing import Dict, Any
from .formatter import print_and_write, write_view_differences

# Compares entities from two databases, identifying unique and differing entities, and generates a markdown report detailing these differences.

def compare_entities(entity1_list, entity2_list, entity_name, log_subdir):
    entity1_dict = {entity['name']: entity for entity in entity1_list}
    entity2_dict = {entity['name']: entity for entity in entity2_list}
    unique_to_db1 = []
    unique_to_db2 = []
    differences_exist = False

    diff_file = os.path.join(log_subdir, f"{entity_name}.md")
    with open(diff_file, 'w') as output:
        print_and_write(f"# {entity_name.capitalize()} Differences", output)

        for name in entity1_dict:
            if name not in entity2_dict:
                unique_to_db1.append(name)
            else:
                differences = []
                for key in entity1_dict[name]:
                    if key in entity2_dict[name] and entity1_dict[name][key] != entity2_dict[name][key]:
                        differences.append((key, entity1_dict[name][key], entity2_dict[name][key]))
                        differences_exist = True

        for name in entity2_dict:
            if name not in entity1_dict:
                unique_to_db2.append(name)

        if unique_to_db1:
            print_and_write(f"\n## {entity_name.capitalize()} only in DB1:", output)
            for name in unique_to_db1:
                print_and_write(f"- {name}", output)

        if unique_to_db2:
            print_and_write(f"\n## {entity_name.capitalize()} only in DB2:", output)
            for name in unique_to_db2:
                print_and_write(f"- {name}", output)

        if differences_exist:
            print_and_write("\n## Difference Details", output)
            for name in entity1_dict:
                if name in entity2_dict:
                    differences = []
                    for key in entity1_dict[name]:
                        if key in entity2_dict[name] and entity1_dict[name][key] != entity2_dict[name][key]:
                            differences.append((key, entity1_dict[name][key], entity2_dict[name][key]))

                    if differences:
                        print_and_write(f"\n### {entity_name.capitalize()}: {name}", output)
                        for key, value1, value2 in differences:
                            print_and_write(f"- **{key}**:\n  - DB1: {value1}\n  - DB2: {value2}", output)

def compare_databases(client1, client2, summary1: Dict[str, Any], summary2: Dict[str, Any], log_dir: str) -> None:
    collections1 = set(summary1['collection_details'].keys())
    collections2 = set(summary2['collection_details'].keys())

    unique_to_db1 = collections1 - collections2
    unique_to_db2 = collections2 - collections1
    matching_collections = collections1 & collections2

    mismatched_collections = []

    db_name = summary1['db_name']
    date_str = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
    log_subdir = os.path.join(log_dir, f"{db_name}-{date_str}")
    os.makedirs(log_subdir, exist_ok=True)
    output_file = os.path.join(log_subdir, "summary.md")

    output = open(output_file, 'w') if output_file else None

    compare_entities(summary1['analyzers'], summary2['analyzers'], 'analyzers', log_subdir)
    compare_entities(summary1['graphs'], summary2['graphs'], 'graphs', log_subdir)
    compare_entities(summary1['views'], summary2['views'], 'views', log_subdir)
    # compare_entities(summary1['indexes'], summary2['indexes'], 'indexes', log_subdir)

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


