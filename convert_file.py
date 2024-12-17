# Covnerts an XML data export from vistadb to JSON

import argparse
import json
import os
from pathlib import Path

import xmltodict

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file", type=Path, help="XML file to convert to JSON")

    args = parser.parse_args()
    xml_path = args.file

    if not xml_path.exists():
        print(f"File not found: {xml_path.relative_to(os.getcwd())}")
        exit(1)

    with xml_path.open(mode="rb") as f:
        data = f.read()
        data_dict = xmltodict.parse(data)

        json_path = xml_path.with_suffix(".json")
        with json_path.open(mode="w") as f2:
            f2.write(json.dumps(data_dict, indent=4))
            print("File Converted")
