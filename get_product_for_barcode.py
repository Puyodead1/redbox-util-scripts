# gets the product for a given barcode

import argparse
import os
from pathlib import Path

from construct import Container
from rich import print
from rich.tree import Tree

from Archive import Archive
from slpp import slpp as lua
from vista import VistaHelper

inv_path = Path(os.getcwd(), "data_files", "inventory.data")
vdb_path = Path(os.getcwd(), "data_files", "profile.data.vdb3")


def dict_to_tree(d, tree=None, root_name=None):
    if tree is None:
        tree = Tree(root_name if root_name else "root")
    for key, value in d.items():
        if isinstance(value, dict):
            subtree = tree.add(f"[bold]{key}[/bold]")
            dict_to_tree(value, subtree)
        else:
            tree.add(f"{key}: {value}")
    return tree


def container_to_tree(container, tree=None):
    """
    Recursively converts a construct.Container into a rich Tree.
    """
    if tree is None:
        tree = Tree("root")

    for key, value in container.items():
        if isinstance(value, Container):  # If the value is another Container
            subtree = tree.add(f"[bold]{key}[/bold]")
            container_to_tree(value, subtree)
        elif isinstance(value, dict):  # If the value is a dictionary
            subtree = tree.add(f"[bold]{key}[/bold]")
            container_to_tree(value, subtree)
        elif isinstance(value, list):  # If the value is a list
            subtree = tree.add(f"[bold]{key}[/bold]")
            for i, item in enumerate(value):
                if isinstance(item, (Container, dict)):
                    container_to_tree(item, subtree.add(f"[bold]Item {i}[/bold]"))
                else:
                    subtree.add(f"Item {i}: {item}")
        else:  # For primitive types
            tree.add(f"{key}: {value}")

    return tree


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # get the product id from the command line
    parser.add_argument("barcode", type=str, help="Barcode to search for")
    args = parser.parse_args()
    barcode = args.barcode

    print(f"Searching for barcode {barcode}")

    archive = Archive.open(inv_path)
    index = archive.find_index(barcode)
    if index:
        item = archive.read_inventory(index)
        print(container_to_tree(item))
        print()
        print("Getting product...")

        vista = VistaHelper(vdb_path)
        # query = f"SELECT [Value] FROM ProductCatalog WHERE [Key] = {item.title_id}"
        query = "SELECT [Value] FROM ProductCatalog WHERE [Key] = " + str(item.title_id)
        product = vista.get_value(query)
        if product:
            decoded = lua.decode(product)
            print(dict_to_tree(decoded, root_name="Product"))
        else:
            print("Product not found")
    else:
        print("Barcode not found")
