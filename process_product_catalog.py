import json

from slpp import slpp as lua

with open("./ProductCatalogFull.json", "r") as f:
    items = json.load(f)["_x002E_vdb3"]["ProductCatalog"]

    # # sort items by Key
    items = sorted(items, key=lambda x: int(x["Key"]))
    items = [lua.decode(x["Value"]) for x in items]

    # # find item where long_name is "Replacement Case"
    # # replacement_case = next((x for x in items if x["long_name"] == "Replacement Case"), None)

    # print(items[-1])

    # find items where long_name does not equal short_name
    items = [x for x in items if x["long_name"] != x["sort_name"]]
    for item in items:
        print(f"Long name:\n\t{item['long_name']}\nSort Name:\n\t{item['sort_name']}\n")
