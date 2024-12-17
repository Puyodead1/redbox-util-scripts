# gets the product id for a given barcode

import argparse
import os
from pathlib import Path

from Archive import Archive

inv_path = Path(os.getcwd(), "data_files", "inventory.data")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # get the product id from the command line
    parser.add_argument("barcode", type=str, help="Barcode to search for")
    args = parser.parse_args()
    barcode = args.barcode

    archive = Archive.open(inv_path)
    index = archive.find_index(barcode)
    if index:
        item = archive.read_inventory(index)
        print(item)
