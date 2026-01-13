# credit to zach3697 on discord for this

import os
import sys
from pathlib import Path

import clr

# add the current directory to the system path
sys.path.append(os.getcwd())
# Load the VistaDB DLL
clr.AddReference("VistaDB.NET20")

from System import Array, Byte
from System.IO import FileAccess, FileMode, FileStream
from VistaDB import VistaDBType

# Import the VistaDB namespaces
from VistaDB.Provider import VistaDBConnection, VistaDBParameter
from VistaDB.VistaDBTypes import VistaDBBinary


class VistaHelper:
    def __init__(self, file):
        # Connection setup
        self.connection_string = f"Data Source={file}"
        self.connection = VistaDBConnection(self.connection_string)

    def search_products(self, search_term, table_name="ProductCatalog"):
        result = []
        reader = None
        try:
            self.connection.Open()
            command = self.connection.CreateCommand()

            command.CommandText = f"""
            SELECT [Key], Value
            FROM {table_name}
            WHERE LOWER(Value) LIKE @exact
            OR LOWER(Value) LIKE @startsWith
            OR LOWER(Value) LIKE @endsWith  
            OR LOWER(Value) LIKE @contains
            """

            search_lower = search_term.lower()

            param1 = command.CreateParameter()
            param1.ParameterName = "@exact"
            param1.Value = f'%name"] = "{search_lower}"%'
            command.Parameters.Add(param1)

            param2 = command.CreateParameter()
            param2.ParameterName = "@startsWith"
            param2.Value = f'%name"] = "{search_lower} %'
            command.Parameters.Add(param2)

            param3 = command.CreateParameter()
            param3.ParameterName = "@endsWith"
            param3.Value = f'%name"] = "% {search_lower}"%'
            command.Parameters.Add(param3)

            param4 = command.CreateParameter()
            param4.ParameterName = "@contains"
            param4.Value = f'%name"] = "% {search_lower} %'
            command.Parameters.Add(param4)

            reader = command.ExecuteReader()

            while reader.Read():
                result.append(
                    (
                        str(reader["Key"]),
                        str(reader["Value"]),
                    )
                )

        except Exception as e:
            print(f"Error: {e}")

        finally:
            if reader:
                reader.Close()
            if self.connection.State == "Open":
                self.connection.Close()

        return result

    def get_value_with_params(self, query, params: dict = {}):
        """
        Generic method to execute SELECT queries with parameters
        """
        result = []
        reader = None
        try:
            self.connection.Open()
            command = self.connection.CreateCommand()
            command.CommandText = query

            # Clear parameters to avoid duplicates
            command.Parameters.Clear()

            # Add parameters
            for key, value in params.items():
                command.Parameters.AddWithValue(key, value)

            reader = command.ExecuteReader()

            while reader.Read():
                row_dict = {}
                for i in range(reader.FieldCount):
                    row_dict[reader.GetName(i)] = str(reader[i])
                result.append(row_dict)

        except Exception as e:
            print(f"Error: {e}")

        finally:
            if reader:
                reader.Close()
            if self.connection.State == "Open":
                self.connection.Close()

        return result

    def get_value(self, query):
        value_string = None
        try:

            self.connection.Open()
            command = self.connection.CreateCommand()
            command.CommandText = query

            reader = command.ExecuteReader()

            while reader.Read():
                value_string = str(reader["Value"])

        except Exception as e:
            print(e)

        finally:
            if reader:
                reader.Close()
            if self.connection.State == "Open":
                self.connection.Close()
        return value_string

    def get_key_list(self, query):
        result = []
        try:

            self.connection.Open()
            command = self.connection.CreateCommand()
            command.CommandText = query

            reader = command.ExecuteReader()

            while reader.Read():
                result.append(str(reader["Key"]))

        except Exception as e:
            print(f"Error: {e}")

        finally:
            # Clean up resources
            if reader:
                reader.Close()
            if self.connection.State == "Open":
                self.connection.Close()
        return result

    def put_value(self, query, values: dict = {}):
        try:

            # Open the database connection
            self.connection.Open()
            command = self.connection.CreateCommand()
            command.CommandText = query

            # Clear parameters to avoid duplicate entries
            command.Parameters.Clear()

            # Create parameters based on the values dictionary
            for key, value in values.items():
                if key == "@img":
                    # Open the file and read its contents into a byte array
                    fs = FileStream(value, FileMode.Open, FileAccess.Read)
                    file_length = int(fs.Length)
                    file_data = Array[Byte](
                        file_length
                    )  # Create a .NET byte array of the required length
                    fs.Read(
                        file_data, 0, file_length
                    )  # Read the file into the byte array
                    fs.Close()  # Close the FileStream

                    # Create parameters
                    blob_param = command.CreateParameter()
                    blob_param.ParameterName = key
                    blob_param.VistaDBType = VistaDBType.Image
                    blob_param.Value = VistaDBBinary(file_data)
                else:
                    command.Parameters.AddWithValue(key, value)  # Add other parameters

            # Execute the query and read the results
            reader = command.ExecuteNonQuery()

        except Exception as e:
            # Print any errors that occur
            print(f"Error: {e}")

        finally:
            # Clean up resources
            if self.connection.State == "Open":
                self.connection.Close()
        return reader


if __name__ == "__main__":
    vdb_path = Path(os.getcwd(), "data_files", "profile.data.vdb3")
    vista = VistaHelper(vdb_path)
    i = vista.get_value(
        "SELECT * FROM ProductCatalog WHERE value LIKE '{ product_id = 1002 ,%'"
    )
    print(i)
