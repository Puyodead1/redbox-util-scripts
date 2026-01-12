from pathlib import Path

from Archive import Archive

if __name__ == "__main__":
    inv_path = Path(r"U:\samples\data_files\inventory.data")

    if not inv_path.exists():
        print(f"Inventory File not found: {inv_path}")
        exit(1)

    archive = Archive.open(inv_path)
    archive.rebuild()
