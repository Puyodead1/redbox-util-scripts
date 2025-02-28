import csv
import json
import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Union

from Archive import Archive
from slpp import slpp as lua

inv_path = Path(os.getcwd(), "data_files", "inventory.data")


class Item:
    def __init__(self, deck: int, slot: int, barcode: Union[str, None]):
        self.deck: int = deck
        self.slot: int = slot
        self.barcode: str = barcode
        self.product_id: Union[int, None] = None
        self.title: Union[str, None] = None

    def __str__(self):
        return f"Deck: {self.deck}, Slot: {self.slot}, Barcode: {self.barcode}, ProductId: {self.product_id}, Title: {self.title}"

    def __repr__(self):
        return self.__str__()

    def __dict__(self):
        return {
            "deck": self.deck,
            "slot": self.slot,
            "barcode": self.barcode,
            "product_id": self.product_id,
            "title": self.title,
        }


with open("./disks.csv", "r") as f:
    barcodes = sqlite3.connect("./data_files/barcodes.db")
    profile = sqlite3.connect("./data_files/profile.data.db")

    csv_reader = csv.reader(f)
    rows = list(csv_reader)
    rows = rows[1:]
    items: List[Item] = []

    with open("./disks_titles.csv", "w") as f2:
        f2.write("Deck,Slot,Barcode,Title\n")

        for i, row in enumerate(rows):
            if i == 0:
                continue
            deck = int(row[0])
            slot = int(row[1])
            barcode = row[2][1:-1]
            if barcode == "EMPTY":
                continue

            item = Item(deck, slot, barcode)
            items.append(item)
        print(f"Total items: {len(items)}")

        placeholders = ", ".join("?" for _ in items)
        query = f"SELECT Barcode, ProductId FROM barcodes WHERE Barcode IN({placeholders})"

        try:
            with barcodes:
                cursor = barcodes.cursor()
                a = [x.barcode for x in items]
                cursor.execute(query, a)
                barcodes_rows = cursor.fetchall()

                for row in barcodes_rows:
                    bc = row[0]
                    pid = row[1]

                    item = next((x for x in items if x.barcode == bc), None)
                    if item:
                        item.product_id = pid
                    else:
                        print(f"Item not found: {bc}")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            barcodes.close()

        placeholders = ", ".join("?" for _ in items)
        query = f"SELECT Value FROM ProductCatalog WHERE Key IN ({placeholders})"

        final = []

        try:
            with profile:
                cursor = profile.cursor()
                a = [x.product_id for x in items]
                print(f"Total product ids: {len(a)}")

                batch_size = 10  # Set batch size to 10
                i = 0

                # Process the IDs in chunks of 'batch_size'
                for i in range(0, len(a), batch_size):
                    batch = a[i : i + batch_size]
                    placeholders = ", ".join("?" for _ in batch)
                    query = f"SELECT Value FROM ProductCatalog WHERE Key IN ({placeholders})"

                    print(f"Querying batch {i//batch_size + 1} of {len(a)//batch_size + 1}...")

                    try:
                        cursor.execute(query, batch)
                        results = cursor.fetchall()

                        i += len(results)

                        for row in results:
                            value = row[0]
                            decoded = lua.decode(value)
                            title = decoded["long_name"]
                            product_id = decoded["product_id"]

                            item = next((x for x in items if x.product_id == product_id), None)
                            if item:
                                item.title = title
                                items.remove(item)
                                items.append(item)
                            else:
                                print(f"Item not found: {product_id}")

                    except sqlite3.Error as e:
                        print(f"An error occurred while processing batch {i//batch_size + 1}: {e}")

        except sqlite3.Error as e:
            print(f"An error occurred: {e}")

        finally:
            profile.close()

        print(i)

        # sort by deck, slot
        items.sort(key=lambda x: (x.deck, x.slot))

        for item in items:
            if item.title == None:
                print(f"Title not found for: {item.barcode}")
                continue
            f2.write(f"{item.deck},{item.slot},'{item.barcode}','{item.title}'\n")
