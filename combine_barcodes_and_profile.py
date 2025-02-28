import os
import sqlite3
from pathlib import Path

barcodes_path = Path(os.getcwd(), "data_files", "barcodes.db")
data_path = Path(os.getcwd(), "data_files", "data.db")

if __name__ == "__main__":

    if not data_path.exists():
        print("Product Database not found")
        exit(1)

    data_db = sqlite3.connect(str(data_path))

    data_cur = data_db.cursor()

    # copy barcodes table into data_db
    data_cur.execute("ATTACH DATABASE ? AS barcodes_db", (str(barcodes_path),))
    data_cur.execute("CREATE TABLE Barcodes AS SELECT * FROM barcodes_db.barcodes")

    data_db.commit()
    data_db.close()
