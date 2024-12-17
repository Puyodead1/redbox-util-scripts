# Replaces a replacement title barcode with the given product id

import argparse
import os
from pathlib import Path

from Archive import Archive

file_path = Path(os.getcwd(), "..", "data_files", "inventory.data")

if __name__ == "__main__":
    if not file_path.exists():
        print(f"File not found: {file_path.relative_to(os.getcwd())}")
        exit(1)

    parser = argparse.ArgumentParser()
    # get the product id from the command line
    parser.add_argument("product_id", type=int, help="Product ID to search for")
    args = parser.parse_args()

    new_pid = args.product_id

    archive = Archive.open(file_path)
    index = archive.linear_search_for_product_id(1139)
    item = archive.read_inventory(index)

    # change the item id
    item["title_id"] = new_pid

    archive.write_inventory(index, item)
    print("Item updated successfully!")

    print(item["barcode"]["barcode"])
