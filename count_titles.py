# a testing script for counting things

import json

with open("./ProductCatalogParsed.json", "r") as f:
    data = json.load(f)

    # # filter out product_type_id that is not 1, 2 or 19
    data = [d for d in data if d["product_type_id"] not in [1, 2, 19]]

    # # count the number of titles for each product_type_id
    # count = {}
    # for d in data:
    #     if d["product_type_id"] not in count:
    #         count[d["product_type_id"]] = 0
    #     count[d["product_type_id"]] += 1

    # # 1 = dvd, 2 = bluray, 19 = 4k
    # # print the result
    # print("DVD: ", count[1])
    # print("BluRay: ", count[2])
    # print("4K: ", count[19])

    # filter product type id 19
    # data = [d for d in data if d["product_type_id"] == 2]
    # sort by sort_name
    data = sorted(data, key=lambda x: x["sort_name"])

    with open("game_list.txt", "w") as f:
        for i in data:
            print(i["long_name"])
            f.write(i["long_name"] + "\n")
