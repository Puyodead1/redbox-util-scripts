import os
import sqlite3
from pathlib import Path

from tqdm import tqdm

from Archive import Archive

db_path = Path(os.getcwd(), "data_files", "barcodes.db")
inv_path = Path(os.getcwd(), "data_files", "inventory.data")

if __name__ == "__main__":
    if db_path.exists():
        print("Removing existing database...")
        db_path.unlink()
    archive = Archive.open(inv_path)
    count = archive.get_number_of_records()
    db = sqlite3.connect(str(db_path))
    cur = db.cursor()
    # create a table with auto incrementing id, barcode and product_id
    cur.execute("CREATE TABLE barcodes (Id INTEGER PRIMARY KEY, Barcode TEXT, ProductId INTEGER)")

    bar = tqdm(total=count, desc="Processing", unit="records", unit_scale=True)

    rep_count = 0
    for i in range(count):
        barcode = archive.read_barcode(i)
        product_id = archive.read_product_id(i)
        if product_id == 1139:
            rep_count += 1
            bar.update(1)
            continue

        # builk insert
        cur.execute("INSERT INTO barcodes(Barcode, ProductId) VALUES (?, ?)", (barcode, product_id))

        bar.update(1)

    bar.close()

    print(f"Skipped {rep_count} records with ProductId 1139")
    print("Committing changes...")

    db.commit()
    db.close()
