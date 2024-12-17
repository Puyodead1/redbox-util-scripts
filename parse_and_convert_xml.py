# takes a converted XML -> JSON VDB export and converts the lua table values to JSON

import argparse
import json
from pathlib import Path

import xmltodict

from slpp import slpp as lua

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Store.json to StoreParsed.json")
    parser.add_argument("file", type=Path, help="Path to exported XML file")

    args = parser.parse_args()

    file = args.file

    if not file.exists():
        raise FileNotFoundError(f"File {file} not found")

    base_name = file.stem
    parsed_path = file.parent / f"{base_name}Parsed.json"

    with open(file, "r", encoding="utf-8", errors="ignore") as f:
        data = xmltodict.parse(f.read())
        a = data["_x002E_vdb3"]
        # get first key not starting with @
        key = [x for x in a.keys() if not x.startswith("@")][0]
        items = [x["Value"] for x in data["_x002E_vdb3"][key]]

        new_items = []
        i = 0
        for item in items:
            if i % 100 == 0:
                print(f"Processing item {i + 1}/{len(items)}")
            new_items.append(lua.decode(item))

            i += 1

        with open(parsed_path, "w") as f2:
            f2.write(json.dumps(new_items, indent=4))
