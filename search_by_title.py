import argparse
import os
from pathlib import Path

from vista import VistaHelper
from slpp import slpp as lua

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add new barcodes to inventory data file."
    )
    # query param
    parser.add_argument("query", type=str, help="Search query for product title")

    args = parser.parse_args()
    query = args.query

    vdb_path = Path(r"U:\samples\data_files\profile.data.vdb3")

    if not vdb_path.exists():
        print(f"Profile Data File not found: {vdb_path}")
        exit(1)

    vista = VistaHelper(vdb_path)

    def search(query):
        print(f"Searching for '{query}'...")
        results = vista.search_products(query)
        if not results:
            print(f"No results found for query: {query}")
            return
        if len(results) > 10:
            print(
                f"More than 10 results found ({len(results)}) for {query}. Refine search"
            )
            return
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
            description = description[:300] + ("..." if len(description) > 300 else "")

            print(f"ID: {key}")
            print(f"Title: {long_name} ({release_year})")
            print(f"Description: {description}")
            print(f"Studio: {studio}")
            print(f"Cast: {', '.join(cast) if cast else 'N/A'}")
            print("-" * 40)
            print("\n")

    search(query)
