# Builds a VistaDB database from the SQLite profile database

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

from System import Array, Byte, Int32, String
from VistaDB.Provider import VistaDBCommand, VistaDBConnection, VistaDBParameter


def create_db(path):
    vistadb_conn = VistaDBConnection()
    vistadb_cmd = VistaDBCommand()

    vistadb_cmd.Connection = vistadb_conn
    vistadb_cmd.CommandText = f"CREATE DATABASE '{path}', PAGE SIZE 1, LCID 1033, CASE SENSITIVE FALSE;"
    vistadb_cmd.ExecuteNonQuery()

    vistadb_conn.Close()


def convert(sqlite_path, vistadb_path):
    create_db(vistadb_path)

    vistadb_conn_str = f"Data Source={vistadb_path}"
    vistadb_conn = VistaDBConnection(vistadb_conn_str)
    vistadb_conn.Open()

    sqlite_conn = sqlite3.connect(str(sqlite_path))
    sqlite_cursor = sqlite_conn.cursor()

    def convert_value_to_vistadb(value, data_type=None):
        """Convert SQLite data to VistaDB-compatible types."""
        if value is None:
            return None
        elif isinstance(value, str):
            # If the value is a JSON string (i.e., Lua table), decode it
            if value.startswith("{") and value.startswith("["):
                decoded_value = json.loads(value)
                a = lua.encode(decoded_value)
                return String(a)

            return String(value)
        elif isinstance(value, int):
            return Int32(value)
        elif isinstance(value, float):
            return value  # Leave floats as-is
        elif isinstance(value, bytes):  # Handle BLOB (Image) data
            # convert to System.Drawing.Image
            return Array[Byte](value)
        else:
            return String(str(value))

    try:
        # Retrieve table names from SQLite
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = sqlite_cursor.fetchall()

        for (table_name,) in tables:
            print(f"Processing table: {table_name}")

            # Retrieve columns from SQLite
            sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
            columns = sqlite_cursor.fetchall()

            # Create table in VistaDB
            column_defs = []
            for column in columns:
                column_name = column[1]
                sqlite_type = column[2]

                # Map SQLite types to VistaDB types
                if "TEXT" in sqlite_type:
                    vista_type = "TEXT"
                elif "BLOB" in sqlite_type:
                    vista_type = "IMAGE"  # Images in SQLite are typically BLOBs in VistaDB
                elif "INTEGER" in sqlite_type:
                    vista_type = "INTEGER"
                else:
                    vista_type = "TEXT"  # Default to TEXT for unhandled types

                column_defs.append(f"{column_name} {vista_type}")

            # Create table in VistaDB
            cmd = vistadb_conn.CreateCommand()
            cmd.CommandText = f"CREATE TABLE {table_name} ({', '.join(column_defs)})"
            cmd.ExecuteNonQuery()

            # Retrieve data from SQLite and insert into VistaDB
            sqlite_cursor.execute(f"SELECT * FROM {table_name}")
            rows = sqlite_cursor.fetchall()

            for row in rows:
                converted_row = tuple(convert_value_to_vistadb(value, data_type=None) for value in row)

                # Prepare insert command
                placeholders = ", ".join([f"@p{i}" for i in range(len(converted_row))])
                cmd.CommandText = f"INSERT INTO {table_name} VALUES ({placeholders})"
                cmd.Parameters.Clear()
                for i, value in enumerate(converted_row):
                    cmd.Parameters.Add(f"@p{i}", value)
                cmd.ExecuteNonQuery()

    finally:
        # Close connections
        sqlite_conn.close()
        vistadb_conn.Close()


if __name__ == "__main__":
    print("Building database, this might take a few minutes")

    sqlite_file = Path(os.getcwd(), "data_files", "profile.data.db")
    vistadb_file = Path(os.getcwd(), "data_files", "profile.data")

    # clean old VistaDB file
    if vistadb_file.exists():
        vistadb_file.rename(vistadb_file.with_suffix(".old"))

    convert(sqlite_file, vistadb_file)
    print("Build Complete!")
