# Converts VistaDB profile database to SQLite

import json
import os
import sqlite3
from pathlib import Path

import clr

from slpp import slpp as lua

vista_path = Path(os.getcwd(), "VistaDB.NET20.dll")
if not vista_path.exists():
    raise FileNotFoundError(f"VistaDB library not found at: {vista_path}")
clr.AddReference(str(vista_path))

from VistaDB.Provider import VistaDBConnection

CREATE_TABLES = {
    "Banner": "CREATE TABLE Banner (Id TEXT, Name TEXT)",
    "Cache": "CREATE TABLE Cache (Name TEXT, Data BLOB, Type INTEGER, Size INTEGER)",
    "Genres": "CREATE TABLE Genres (Id TEXT, Name TEXT)",
    "Market": "CREATE TABLE Market (Id TEXT, Name TEXT)",
    "ProductCatalog": """
        CREATE TABLE "ProductCatalog" (
            "Id"	INTEGER NOT NULL UNIQUE,
            "BoxOfficeGross"	INTEGER NOT NULL,
            "ClosedCaptioned"	INTEGER NOT NULL,
            "ComingSoonDays"	INTEGER NOT NULL,
            "Description"	TEXT NOT NULL,
            "Directors"	TEXT,
            "DoNotRentDate"    TEXT,
            "Genres"	TEXT,
            "ImageFile"	TEXT,
            "LongName"	TEXT NOT NULL,
            "MerchandiseDate"	TEXT NOT NULL,
            "NationalStreetDate"	TEXT,
            "NumberOfPlayersText" TEXT,
            "ProductTypeId"	INTEGER NOT NULL,
            "RatingId"	TEXT NOT NULL,
            "RedboxPlusEligibleDate"    TEXT,
            "ReleaseDate"	TEXT NOT NULL,
            "RunningTime"	TEXT NOT NULL,
            "SellThru"	INTEGER NOT NULL,
            "SellThruNew"	INTEGER NOT NULL,
            "SellThruDate"	TEXT,
            "SellThruPrice"	NUMERIC,
            "SortDate"	TEXT NOT NULL,
            "SortName"	TEXT NOT NULL,
            "Starring"	TEXT,
            "Stars"	INTEGER,
            "Studio"	INTEGER
        );
        """,
    "ProductRating": """
        CREATE TABLE "ProductRating" (
            "Id"	INTEGER NOT NULL UNIQUE,
            "ProductFamilyId"	INTEGER NOT NULL,
            "Name"	TEXT NOT NULL,
            "RatingDescription"	TEXT NOT NULL
        );
        """,
    "ProductType": """
        CREATE TABLE "ProductType" (
            "Id"	INTEGER NOT NULL UNIQUE,
            "ProductFamilyId"	INTEGER NOT NULL,
            "ProductTypeName"	TEXT NOT NULL
        );
        """,
    "Store": """CREATE TABLE `Store` (
            `Id`	TEXT NOT NULL UNIQUE,
            `Address`	TEXT NOT NULL,
            `ReturnTime`	TEXT NOT NULL,
            `RentalTaxRate`	NUMERIC,
            `PurchaseTaxRate`	NUMERIC,
            `PurchasePrice`	NUMERIC NOT NULL,
            `VendorId`	INTEGER,
            `MarketId`	INTEGER,
            `BannerId`	INTEGER,
            `SellThru`	INTEGER NOT NULL,
            `OpenDate`	TEXT,
            `InvSync`	INTEGER NOT NULL,
            `Address1`	TEXT,
            `Address2`	TEXT,
            `City`	TEXT,
            `County`	TEXT,
            `State`	TEXT,
            `Zip`	TEXT,
            `CollectionMethod`	INTEGER,
            `DigitalPurchaseTaxRate`	NUMERIC,
            `ServiceFee`	NUMERIC,
            `ServiceFeeTaxRate`	NUMERIC,
            `ReturnOnlyModeDate`	INTEGER,
            PRIMARY KEY(`Id`)
        );""",
    "Vendor": "CREATE TABLE Vendor (Id TEXT, Name TEXT)",
}


def convert(vistadb_path, sqlite_path):
    vistadb_conn_str = f"Data Source={vistadb_path}"
    vistadb_conn = VistaDBConnection(vistadb_conn_str)
    vistadb_conn.Open()

    sqlite_conn = sqlite3.connect(sqlite_path)
    cursor = sqlite_conn.cursor()

    # create tables
    for table_name, create_sql in CREATE_TABLES.items():
        cursor.execute(create_sql)

    def convert_value(value, data_type=None):
        if value is None:
            return None
        elif isinstance(value, str):
            # try to decode lua tables
            if value.startswith("{") and value.startswith("["):
                value = lua.decode(value)
                return json.dumps(value)

            return value
        elif isinstance(value, (int, float, str)):
            return value
        elif isinstance(value, bytes):
            return value
        elif hasattr(value, "ToArray"):
            return bytes(value.ToArray())
        elif data_type and "image" in data_type.lower():
            return bytes(value)
        else:
            print(f"Unhandled data type: {type(value)}")
            return str(value)

    try:
        table_names = [
            "Banner",
            "Cache",
            "Genres",
            "Market",
            "ProductCatalog",
            "ProductRating",
            "ProductType",
            "Store",
            "Vendor",
        ]
        for table_name in table_names:
            print(f"Processing table: {table_name}")

            data_cmd = vistadb_conn.CreateCommand()
            data_cmd.CommandText = f"SELECT * FROM {table_name}"
            data_reader = data_cmd.ExecuteReader()

            column_defs = []
            if table_name == "Cache":
                for i in range(data_reader.FieldCount):
                    column_name = data_reader.GetName(i)
                    data_type = data_reader.GetDataTypeName(i)

                    if "char" in data_type.lower() or "text" in data_type.lower():
                        sqlite_type = "TEXT"
                    elif "byte[]" in data_type.lower() or "blob" in data_type.lower() or "image" in data_type.lower():
                        sqlite_type = "BLOB"  # Correctly store binary data as BLOB
                    elif "int" in data_type.lower() or "numeric" in data_type.lower():
                        sqlite_type = "INTEGER"
                    else:
                        sqlite_type = "TEXT"  # Default to TEXT for unhandled types

                    column_defs.append(f"{column_name} {sqlite_type}")

            rows = []
            a = {
                "Banner": "banner_name",
                "Genres": "genre_name",
                "Market": "market_name",
                "Vendor": "vendor_name",
            }
            while data_reader.Read():
                # row = tuple(
                #     convert_value(data_reader[i], data_reader.GetDataTypeName(i)) for i in range(data_reader.FieldCount)
                # )
                # row = map_item()
                if table_name not in ["Cache", "Store", "ProductCatalog", "ProductRating", "ProductType"]:
                    v = data_reader[1]
                    v = lua.decode(v)
                    name = v[a[table_name]]
                    row = (data_reader[0], name)
                elif table_name == "Store":
                    Id = data_reader[0]
                    v = data_reader[1]
                    v = lua.decode(v)
                    # strip store_id
                    v.pop("store_id")
                    # convert all keys to CamelCase
                    v = {k[0].upper() + k[1:]: v for k, v in v.items()}
                    row = (Id, *v.values())
                elif table_name == "ProductCatalog":
                    Id = data_reader[0]
                    v = data_reader[1]
                    v = lua.decode(v)

                    bog = v.get("box_office_gross", 0)
                    cc = v.get("closed_captioned", False)
                    csd = v.get("coming_soon_days", 0)
                    desc = v.get("description")
                    directors = v.get("directors")
                    if directors is not None:
                        directors = json.dumps(directors)
                    dnrd = v.get("do_not_rent_date")
                    genres = v.get("genres")
                    if genres:
                        a = genres.keys()
                        genres = json.dumps(list(a))
                    img = v.get("image_file")
                    lname = v.get("long_name")
                    merchdate = v.get("merchandise_date")
                    nsd = v.get("national_street_date")
                    npt = v.get("number_of_players_text")
                    ptid = v.get("product_type_id")
                    rid = v.get("rating_id")
                    rped = v.get("redbox_plus_eligible_date")
                    rd = v.get("release_date")
                    rt = v.get("running_time")
                    st = v.get("sell_thru")
                    stn = v.get("sell_thru_new")
                    std = v.get("sellthru_date")
                    stp = v.get("sellthru_price")
                    sortdate = v.get("sort_date")
                    sname = v.get("sort_name")
                    starring = v.get("starring")
                    if starring is not None:
                        starring = json.dumps(starring)
                    stars = v.get("stars")
                    studio = v.get("studio")

                    row = (
                        Id,
                        bog,
                        cc,
                        csd,
                        desc,
                        directors,
                        dnrd,
                        genres,
                        img,
                        lname,
                        merchdate,
                        nsd,
                        npt,
                        ptid,
                        rid,
                        rped,
                        rd,
                        rt,
                        st,
                        stn,
                        std,
                        stp,
                        sortdate,
                        sname,
                        starring,
                        stars,
                        studio,
                    )
                elif table_name == "ProductRating":
                    Id = data_reader[0]
                    v = data_reader[1]
                    v = lua.decode(v)
                    pfid = v.get("product_family_id")
                    name = v.get("name")
                    desc = v.get("rating_description")

                    row = (Id, pfid, name, desc)
                elif table_name == "ProductType":
                    Id = data_reader[0]
                    v = data_reader[1]
                    v = lua.decode(v)
                    pfid = v.get("product_family_id")
                    name = v.get("product_type_name")

                    row = (Id, pfid, name)
                elif table_name == "Cache":
                    row = tuple(
                        convert_value(data_reader[i], data_reader.GetDataTypeName(i))
                        for i in range(data_reader.FieldCount)
                    )

                rows.append(row)

            if rows:
                placeholders = ", ".join("?" for _ in rows[0])
                insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"
                cursor.executemany(insert_sql, rows)

            sqlite_conn.commit()

    finally:
        vistadb_conn.Close()
        sqlite_conn.close()


if __name__ == "__main__":
    print("Converting, this might take a few minutes")
    vistadb_file = "./data_files/profile_fresh.data.vdb3"
    sqlite_file = "./data_files/data.db"

    # clean old sqlite file
    try:
        os.remove(sqlite_file)
    except FileNotFoundError:
        pass

    convert(vistadb_file, sqlite_file)
    print("Conversion Complete!")
