# a testing script for counting some stuff

import json

from slpp import slpp as lua

product_to_barcode: dict[str, list[str]] = {}
barcode_to_product: dict[str, str] = {}
product_catalog: dict = {}
product_catalog_full: dict = {}


def main():
    # with open("./HALData.xml", "r") as f:
    #     data = f.read()
    # data_dict = xmltodict.parse(data)
    # inventory = data_dict["_x002E_vdb3"]["Inventory_v1"]
    # # filter out items with ID of EMPTY
    # filtered = [item for item in inventory if item["ID"] != "EMPTY"]
    # empties = [item for item in inventory if item["ID"] == "EMPTY"]
    # print("Number of items in inventory: ", len(filtered))
    # print("Number of empty slots in inventory: ", len(empties))

    print("Loading ProductToBarcode data...")
    with open("./ProductToBarcode.json", "r") as f:
        data = json.load(f)
        mapping = data["_x002E_vdb3"]["ProductToBarcode"]
        for item in mapping:
            k = item["Key"]
            v = item["Value"]
            v = v.replace("[", "").replace("]", "").replace("=", ":").replace("status", "'status'").replace("'", '"')
            v = json.loads(v)
            v = list(v.keys())
            product_to_barcode[k] = v

            for barcode in v:
                barcode_to_product[barcode] = k

    print(f"Number of products: {len(product_to_barcode)}")

    print("Loading ProductCatalog...")
    with open("./ProductCatalog.json", "r") as f:
        data = json.load(f)
        catalog = data["_x002E_vdb3"]["ProductCatalog"]
        for item in catalog:
            k = item["Key"]
            v = item["Value"]

            parsed = lua.decode(v)
            if not parsed["in_stock"]:
                continue
            product_catalog[k] = parsed

    print("Loading ProductCatalogFull...")
    with open("./ProductCatalogFull.json", "r") as f:
        data = json.load(f)
        catalog = data["_x002E_vdb3"]["ProductCatalog"]
        for item in catalog:
            k = item["Key"]
            v = item["Value"]

            parsed = lua.decode(v)
            product_catalog_full[k] = parsed

    # titles = {}
    titles = []
    duplicates = 0
    print("Loading inventory...")
    with open("./InventoryNew.json", "r") as f:
        inventory = json.load(f)
        data = inventory["_x002E_vdb3"]["Inventory_v1"]
        # filter out items with ID of EMPTY
        filtered = [item["ID"] for item in data if item["ID"] != "EMPTY"]
        # try to find product for each barcode
        filtered = [barcode_to_product.get(item) for item in filtered]

        # for item in filtered:
        #     product = barcode_to_product.get(item)
        #     if product is not None:
        #         # if product not in titles, assign as empty list
        #         if product not in titles:
        #             titles[product] = {
        #                 "title": product_catalog_full[product]["long_name"],
        #                 "count": 1,
        #                 "product_id": product,
        #                 "barcode": item,
        #             }
        #         else:
        #             titles[product]["count"] += 1

        #         # # titles[product].append(product_catalog_full[product]["title"])
        #         # titles.append((product, product_catalog_full[product]["long_name"]))
        #     else:
        #         print(f"Barcode {item} not found in barcode_to_product mapping")

    # sort titles by title field
    # titles = sorted(titles.values(), key=lambda x: x["title"])

    # for i in titles:
    #     # print(i)
    #     if i["count"] > 1:
    #         duplicates += i["count"] - 1

    # print(f"Number of duplicates: {duplicates}")

    # now find all products we dont have in inventory
    missing = []
    for product in product_catalog_full:
        if product_catalog_full[product]["product_type_id"] != 1:
            continue
        if product not in filtered:
            missing.append(product)

    # sort
    missing = sorted(missing, key=lambda x: product_catalog_full[x]["long_name"])
    for product in missing:
        print(product_catalog_full[product]["long_name"])


if __name__ == "__main__":
    main()
