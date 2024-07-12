import json
import argparse
import os
from client import ArangoDBClient
from formatter import Formatter
from comparator import Comparator

def write_discrepancies_to_md(discrepancies, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    collections_md_path = os.path.join(output_dir, "collection_discrepancies.md")
    indexes_md_path = os.path.join(output_dir, "index_discrepancies.md")

    with open(collections_md_path, 'w') as collections_md_file:
        collections_md_file.write("# Collection Discrepancies\n\n")
        collections_md_file.write(json.dumps(discrepancies.get('collections', {}), indent=2))

    with open(indexes_md_path, 'w') as indexes_md_file:
        indexes_md_file.write("# Index Discrepancies\n\n")
        indexes_md_file.write(json.dumps(discrepancies.get('indexes', {}), indent=2))

def main(source_url, target_url, db_name, output_dir):
    source_client = ArangoDBClient(source_url, db_name)
    target_client = ArangoDBClient(target_url, db_name)

    source_entities = source_client.get_all_entities()
    target_entities = target_client.get_all_entities()

    formatter = Formatter()
    formatted_source_entities = formatter.format_entities(source_entities)
    formatted_target_entities = formatter.format_entities(target_entities)

    comparator = Comparator()
    discrepancies = comparator.compare_entities(formatted_source_entities, formatted_target_entities)

    if discrepancies:
        print("Discrepancies found:")
        print(json.dumps(discrepancies, indent=2))
        write_discrepancies_to_md(discrepancies, output_dir)
    else:
        print("No discrepancies found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify ArangoDB instances")
    parser.add_argument("source_url", type=str, help="URL of the source ArangoDB instance")
    parser.add_argument("target_url", type=str, help="URL of the target ArangoDB instance")
    parser.add_argument("db_name", type=str, help="Database name to verify")
    parser.add_argument("output_dir", type=str, help="Directory to save markdown files")

    args = parser.parse_args()
    main(args.source_url, args.target_url, args.db_name, args.output_dir)

