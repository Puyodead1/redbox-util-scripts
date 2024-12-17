# gets a product for a given product id

import argparse
import os
from pathlib import Path

from vista import VistaHelper

vdb_path = Path(os.getcwd(), "data_files", "profile.data.vdb3")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # get the product id from the command line
    parser.add_argument("product_id", type=str, help="Product ID to search for")
    args = parser.parse_args()
    pid = args.product_id

    vista = VistaHelper(vdb_path)
    query = "SELECT [Value] FROM ProductCatalog WHERE [Key] = " + pid
    product = vista.get_value(query)
    print(product)
