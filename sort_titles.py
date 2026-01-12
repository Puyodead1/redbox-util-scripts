import sqlite3
from datetime import datetime

from slpp import slpp as lua

if __name__ == "__main__":
    titles = []
    profile = sqlite3.connect("./data_files/profile.db")

    query = "SELECT * FROM ProductCatalog"

    try:
        with profile:
            cursor = profile.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()

            for k, v in rows:
                v = lua.decode(v)
                if isinstance(v, dict):
                    release_date = v.get("release_date")
                    year = int(release_date[:4])
                    if year > 2025:
                        continue
                    titles.append(v)
                else:
                    print(f"Skipping entry {k} due to missing or invalid Title")

        print(f"Total titles found: {len(titles)}")
        # sort by release_date
        sorted_titles = sorted(titles, key=lambda x: datetime.strptime(x["release_date"], "%Y%m%d%H%M%S"))
        with open("./titles_sorted.json", "w") as f:
            import json

            json.dump(sorted_titles, f, indent=4)
            print("Titles sorted and saved to titles_sorted.json")

        print(json.dumps(sorted_titles[:10], indent=4))

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        profile.close()
