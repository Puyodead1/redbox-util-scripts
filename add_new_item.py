# Interactive script to add a new movie to the database

import hashlib
import os
from pathlib import Path

import requests
from dotenv import load_dotenv
from PIL import Image

from slpp import slpp as lua
from vista import VistaHelper

load_dotenv()

OMDB_API_KEY = os.getenv("OMDB_API_KEY")

inv_path = Path(os.getcwd(), "data_files", "inventory.data")
vdb_path = Path(os.getcwd(), "data_files", "profile.data.vdb3")


class OMDB:
    def __init__(self, api_key):
        self.api_key = api_key
        self.api_base = f"http://www.omdbapi.com"
        self.session = requests.Session()

    def search_for_movie(self, title, year=None):
        params = {"apikey": self.api_key, "t": title, "type": "movie", "r": "json"}
        if year:
            params["y"] = year
        r = self.session.get(self.api_base, params=params)
        if not r.ok:
            return None

        data = r.json()
        if data["Response"] == "False":
            return None

        return data


# rating table to map rating_id to rating name
rating_table = {
    5: "G",
    6: "PG",
    7: "PG-13",
    8: "R",
    10: "NR",
    13: "ALL AGES",
    14: "EC",
    15: "E",
    16: "E 10+",
    17: "T",
    18: "M (17+)",
    19: "RP",
    21: "TVMA",
    22: "TVPG",
    23: "TV14",
    24: "TVG",
    25: "TVY7",
    27: "NC-17",
}

reverse_rating_table = {v: k for k, v in rating_table.items()}
reverse_rating_table["Not Rated"] = 10
reverse_rating_table["N/A"] = 10
reverse_rating_table["Approved"] = 10

genre_table = {
    "Action & Adventure": 1000,
    "Animation": 1001,
    "Award Winners": 1002,
    "Crime": 1003,
    "Comedy": 1004,
    "Drama": 1005,
    "Family": 1006,
    "Foreign": 1007,
    "Holiday": 1008,
    "Horror": 1009,
    "Kids": 1010,
    "Musical": 1011,
    "Romance": 1012,
    "Sci-Fi": 1013,
    "Science Fiction": 1013,
    "Fantasy": 1013,
    "Special Interest": 1014,
    "Suspense": 1016,
    "Thriller": 1016,
    "Televison": 1017,
    "War": 1018,
    "Western": 1019,
    "Hit Movies": 1020,
    "Blu-ray": 1022,
    "Fighting": 1028,
    "Music & Party": 1030,
    "Shooter": 1034,
    "Sports": 1036,
    "Documentary": 1092,
    "Top 20 Movies": 1093,
    "Family": 1094,
    "War & Western": 1098,
    "Martial Arts": 1099,
    "Indepedent": 1100,
    "Documentary & Special Interest": 1101,
    "Adventure": 1102,
    "Action": 1103,
    "New Release": 1105,
}

if __name__ == "__main__":
    if not inv_path.exists():
        print(f"File not found: {inv_path.relative_to(os.getcwd())}")
        exit(1)

    if not OMDB_API_KEY:
        print("OMDB API key not found in environment variables!")
        exit(1)

    title_name = input("Enter the title of the movie: ")
    year = input("Enter the year of the movie (press enter to skip): ")
    # if year is empty, set it to None
    if not year:
        year = None

    # first, get the movie from omdb
    omdb = OMDB(OMDB_API_KEY)
    result = omdb.search_for_movie(title_name, year)

    if not result:
        print("Movie not found!")
        exit()

    print(f"Found movie '{result['Title']} ({result['Year']})'")
    is_correct = input("Is this the correct movie? (y/[n]): ")
    if is_correct.lower() != "y":
        print("Exiting...")
        exit()

    # select type, 1 = dvd, 2 = blu-ray, 3 = 4k uhd
    product_type = int(input("Enter the product type (1=dvd, 2=blu-ray, 19=4k uhd): "))
    if product_type not in [1, 2, 19]:
        print("Invalid product type!")
        exit()

    description = result["Plot"]
    long_name = result["Title"]
    sort_name = result["Title"].replace("The ", "").replace("A ", "").replace("An ", "")

    genres = result["Genre"].split(", ")
    # dict of genre ids as string to True
    genre_dict = {str(genre_table[genre]): True for genre in genres if genre in genre_table}

    if product_type == 2:
        genre_dict["1022"] = True
        sort_name += " (Blu-ray)"
        # long_name += " (Blu-ray)"

    # ask user of the disk is widescreen
    is_widescreen = False
    widescreen = input("Is the movie widescreen? (y/[n]): ")
    if widescreen.lower() == "y":
        is_widescreen = True

    # convert runtime from MM minutes to hours and minutes
    runtime = result["Runtime"].split(" ")[0]
    hours = int(runtime) // 60
    minutes = int(runtime) % 60
    runtime = f"{hours:02}:{minutes:02}"

    # convert Released from DD Mon YYYY to YYYYMMDD, month should be converted from name to number
    released = result["Released"].split(" ")
    month = released[1]
    month_table = {
        "Jan": "01",
        "Feb": "02",
        "Mar": "03",
        "Apr": "04",
        "May": "05",
        "Jun": "06",
        "Jul": "07",
        "Aug": "08",
        "Sep": "09",
        "Oct": "10",
        "Nov": "11",
        "Dec": "12",
    }
    released = f"{released[2]}{month_table[month]}{released[0]}000000"

    # convert box office to a rounded integer
    box_office = result["BoxOffice"]
    if box_office != "N/A":
        box_office = box_office.replace("$", "").replace(",", "")
        box_office = round(float(box_office) / 1000000)
    else:
        box_office = 0

    has_cc = False
    has_cc_r = input("Does the movie have closed captioning? (y/[n]): ")
    if has_cc_r.lower() == "y":
        has_cc = True

    studio = input("Enter the studio: ")

    # find the next available product id
    vista = VistaHelper(str(vdb_path))
    # we need to get a list of all the product ids in the database
    query = "SELECT [Key] FROM ProductCatalog"
    keys = vista.get_key_list(query)
    # sort
    keys = sorted(keys, key=lambda x: int(x))
    # last key
    last_key = int(keys[-1])
    pid = last_key + 1

    description += "\\r\\n\\r\\n"
    description += f"Rated {result['Rated']} by the Motion Pictures of America.\\r\\n"
    if is_widescreen:
        description += "Widescreen\\r\\n\\r\\n"

    # escape the description
    description = description.replace("'", "''")

    # escape the name
    sort_name = sort_name.replace("'", "''")
    safe_title = long_name.replace("'", "''")

    # create a sha-1 hash of the title string from above
    title_hash = hashlib.sha1(result["Title"].encode()).hexdigest().upper()
    cache_key = title_hash + ".jpg"

    # download the movie poster
    r = requests.get(result["Poster"])

    # poster folder path is cache\cache_key
    poster_path = Path("cache") / cache_key
    # ensure the cache folder exists
    poster_path.parent.mkdir(parents=True, exist_ok=True)

    with open(poster_path, "wb") as f:
        f.write(r.content)
    print(f"Poster saved to {poster_path}")

    # resize the poster to 292x370
    img = Image.open(poster_path)
    img = img.resize((292, 370))
    img.save(poster_path)
    print(f"Poster resized to 262x370")

    # next, format the dict with the information we are going to insert
    insert_dict = {
        "box_office_gross": box_office,
        "closed_captioned": has_cc,
        "coming_soon_days": 0,
        "description": description,
        "directors": [result["Director"].replace("'", "''")],
        "genres": genre_dict,
        "image_file": cache_key,
        "long_name": safe_title,
        "merchandise_date": released,
        "national_street_date": released,
        "number_of_players_text": "",
        "product_id": pid,
        "product_type_id": product_type,
        "rating_id": reverse_rating_table[result["Rated"]],
        "release_date": released,
        "running_time": runtime,
        "sell_thru": True,
        "sell_thru_new": False,
        "sellthru_date": "20241001000000",
        "sellthru_price": 0.0,
        "sort_date": released,
        "sort_name": sort_name,
        "starring": [x.replace("'", "''") for x in result["Actors"].split(", ")],
        "stars": round(float(result["imdbRating"])),
        "studio": studio,
    }

    # convert to lua table
    lua_table = lua.encode(insert_dict)

    print(lua_table)

    with open(poster_path, "rb") as f:
        img_data = f.read()

    try:
        query = f"INSERT INTO Cache (Name, Data, Type, Size) VALUES (@Name, @Data, @Type, @Size)"

        command = vista.connection.CreateCommand()
        command.CommandText = query
        # clear parameters
        command.Parameters.Clear()
        # add parameters
        command.Parameters.AddWithValue("@Name", cache_key)
        command.Parameters.AddWithValue("@Data", img_data)
        command.Parameters.AddWithValue("@Type", 0)
        command.Parameters.AddWithValue("@Size", len(img_data))
        reader = command.ExecuteNonQuery()
    except Exception as e:
        print(f"Error: {e}")
        exit(1)

    print("Poster added to Cache table")

    # format the insert query where Key = pid, and Value = lua_table
    query = f"INSERT INTO ProductCatalog ([Key], Value) VALUES ({pid}, '{lua_table}')"
    vista.put_value(query)
    print(f"Successfully added '{result['Title']}' to the database with product id {pid}")
