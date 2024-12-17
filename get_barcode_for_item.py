# Retrieve the barcode for a given product id

import argparse
import os
from pathlib import Path

from Archive import Archive

inv_path = Path(os.getcwd(), "data_files", "inventory.data")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # get the product id from the command line
    parser.add_argument("product_id", type=int, help="Product ID to search for")
    args = parser.parse_args()
    pid = args.product_id

    archive = Archive.open(inv_path)
    index = archive.linear_search_for_product_id(pid)
    if index:
        item = archive.read_inventory(index)
        print(item)
    else:
        print("Nothing found")
