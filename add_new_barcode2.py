import argparse
import os
from pathlib import Path

from Archive import Archive, Barcode, Item, compress_barcode_to_dict
from vista import VistaHelper
from slpp import slpp as lua

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add new barcodes to inventory data file."
    )
    parser.add_argument(
        "--inv", type=Path, required=True, help="Path to inventory.data file"
    )
    parser.add_argument(
        "--vdb", type=Path, required=True, help="Path to profile.data.vdb3 file"
    )
    # description limit
    parser.add_argument(
        "--desc-limit", type=int, default=300, help="Description character limit"
    )
    parser.add_argument(
        "--data",
        type=str,
        nargs="+",
        required=True,
        help="Pairs of barcode and search term, e.g. 123456789 'Movie Title'",
    )
    args = parser.parse_args()
    inv_path = args.inv
    vdb_path = args.vdb
    DESC_LIMIT = args.desc_limit
    DATA = []
    for i in range(0, len(args.data), 2):
        DATA.append(
            {
                "barcode": args.data[i],
                "search": args.data[i + 1],
            }
        )

    print(f"Inventory Path: {inv_path}")
    print(f"Profile Data Path: {vdb_path}")
    print(f"Data to add: {DATA}")

    if not inv_path.exists():
        print(f"Inventory File not found: {inv_path}")
        exit(1)

    if not vdb_path.exists():
        print(f"Profile Data File not found: {vdb_path}")
        exit(1)

    archive = Archive.open(inv_path)
    print(f"Current Record Count: {archive.get_number_of_records():,d}")
    vista = VistaHelper(vdb_path)

    def handle(entry):
        query = entry["search"]
        barcode = entry["barcode"]

        print(f"Searching for '{query}'...")
        results = vista.search_products(query)
        if not results:
            print(f"No results found for query: {query}")
            # prompt for new query or skip
            new_query = input("Enter a new query or press Enter to skip: ")
            if not new_query:
                return
            query = new_query
            handle({"barcode": barcode, "search": query})
            return
        if len(results) > 10:
            print(
                f"More than 10 results found ({len(results)}) for {query}. Refine search"
            )
            # prompt for new query or skip
            new_query = input("Enter a new query or press Enter to skip: ")
            if not new_query:
                return
            query = new_query
            handle({"barcode": barcode, "search": query})
        for i, (key, value) in enumerate(results):
            parsed_item = lua.decode(value)
            long_name = parsed_item["long_name"]
            sort_name = parsed_item["sort_name"]
            release_date = parsed_item["release_date"]
            release_year = release_date[:4]
            description = parsed_item.get("description", "N/A")
            studio = parsed_item.get("studio", "N/A")
            cast = parsed_item.get("starring", [])

            # limit description
            description = description.split("\\r\\n")[0]
            description = description[:DESC_LIMIT] + (
                "..." if len(description) > DESC_LIMIT else ""
            )

            print(f"Result {i + 1}:")
            print(f"Title: {long_name} ({release_year})")
            print(f"Description: {description}")
            print(f"Studio: {studio}")
            print(f"Cast: {', '.join(cast) if cast else 'N/A'}")
            print("-" * 40)
            print("\n")

        # select which one to use, or skip
        selection = int(
            input(f"Select result to use (1-{len(results)}) or 0 to skip: ")
        )
        if selection == 0:
            print("Skipping...")
            exit(0)
        selected_key, selected_value = results[selection - 1]
        product = lua.decode(selected_value)

        print(f'Selected: {product["long_name"]} ({product["release_date"][:4]})')

        # create a new record
        pid = product["product_id"]

        record = {
            "barcode": compress_barcode_to_dict(barcode),
            "title_id": pid,
            "status_code": 0,  # Known
            "total_rental_count": 0,
        }

        archive.add_record(record)
        print(f"Added barcode {barcode} with Product ID {pid} to inventory.")
        print(f"New Record Count: {archive.get_number_of_records():,d}")

    for entry in DATA:
        query = entry["search"]
        barcode = entry["barcode"]

        # ensure the barcode doesnt already exist
        index = archive.find_index(barcode)
        if index != -1:
            print(
                f"Barcode {barcode} already exists in inventory at index {index}. Skipping..."
            )
            continue

        handle(entry)

    archive.close()
