# gets the next available product id

from vista import VistaHelper

if __name__ == "__main__":
    vista = VistaHelper("./profile.data.vdb3")
    # get all the product ids
    query = "SELECT [Key] FROM ProductCatalog"
    keys = vista.get_key_list(query)
    # sort
    keys = sorted(keys, key=lambda x: int(x))
    # last key
    last_key = int(keys[-1])
    pid = last_key + 1

    print(pid)
