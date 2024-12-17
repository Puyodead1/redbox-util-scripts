# gets the product name for a given barcode

import argparse

from Archive import Archive
from slpp import slpp
from vista import VistaHelper

type_map = {1: "DVD", 2: "Blu-ray", 3: "Xbox 360", 19: "4K UHD"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # get the product id from the command line
    parser.add_argument("barcode", type=str, help="Barcode to search for")
    args = parser.parse_args()
    barcode = args.barcode

    vista = VistaHelper("./profile.data.vdb3")

    archive = Archive.open("inventory.data")
    index = archive.find_index(barcode)
    if index:
        item = archive.read_inventory(index)
        pid = str(item.title_id)
        print(f"Product ID: {pid}")
        query = "SELECT [Value] FROM ProductCatalog WHERE [Key] = " + pid
        product = vista.get_value(query)
        if product:
            a = slpp.decode(product)
            name = a["long_name"]
            typ = a["product_type_id"]
            typ_name = type_map.get(typ, "Unknown")
            print(f"{name} [{typ_name}]")
        else:
            print("Product not found")
    else:
        print("Barcode not found")
