import json
import sqlite3

# Open the database
conn = sqlite3.connect("./data_files/data.db")
cursor = conn.cursor()

with open("./data_files/StoreParsed.json", "r") as f:
    store_data = json.load(f)

    # Track addresses and their associated stores
    address_store_map = {}
    for store in store_data:
        store_address = store["address"]
        if store_address not in address_store_map:
            address_store_map[store_address] = [store]
        else:
            address_store_map[store_address].append(store)

    i = 0
    # Find and print addresses with exactly 3 stores having the same banner ID
    for address, stores in address_store_map.items():
        if len(stores) == 3:
            # Check if all 3 banner IDs are the same
            banner_ids = {store["banner_id"] for store in stores}
            openDates = [store["open_date"] for store in stores]
            if len(banner_ids) == 1 and not None in openDates:  # All banner IDs are the same
                print(f"Address: {address}")
                print(f"Store IDs: {[store['store_id'] for store in stores]}")
                print(f"Banner ID: {stores[0]['banner_id']}")  # Same for all stores
                print(f"Open Dates: {openDates}")

                i = i + 1

    print(i)
