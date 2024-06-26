# Uso: python import_to_wp.py <URL de wordpress>
# Lee libros.json y llama wp-cli para agregar todos los libros
# Asume <URL de wordpress>/wp-content/uploads/manual_uploads/{image_filename} como ruta de imagen
# Fallará si no se puede abrir la ruta via request (i.e. si <URL de wordpress> está mal)

import json
import subprocess
from urllib.parse import urlsplit
import itertools
import sys

from dotenv import load_dotenv
import os

load_dotenv()

SIMULTANEOUS_PROCESSES = 10

def add_arg(cli: list[str], key: str, value: str) -> None:
    cli.append(f"--{key}={value}")

# def get_ids() -> dict[str, str]:
#     """Returns a map from original ids to wordpress ids"""
#     result = {}
#     for i in itertools.count(1):
#         print(f"Page {i}")
#         cli = ["wp", "wc", "product", "list", "--format=json", "--fields=id,attributes", "--per_page=100", f"--page={i}"]
#         output = subprocess.run(cli, stdout=subprocess.PIPE).stdout
#         products = json.loads(output)
#         if not products:
#             break
#         for product in products:
#             for attribute in product["attributes"]:
#                 if attribute["name"] == "original_id":
#                     original_id = attribute["options"][0]
#                     result[original_id] = str(product["id"])
#     return result

def handle_processes(processes, id_map) -> bool:
    success = True
    for id, process in processes.items():
        if process.wait():
            success = False
        output = process.stdout.read().decode()
        if output:
            id_map[id] = output.strip()
            with open("id_map.json", "w") as file:
                json.dump(id_map, file)
    return success

def import_to_wordpress(wordpress_url, wordpress_path):
    print("Loading libros.json")
    with open("libros.json") as file:
        libros = json.load(file)

    libros = [libro for libro in libros if libro["product_type"] == "book" and libro["stock_available"]]

    arg_map = {
        "name": "title",
        "slug": "titleFriendly",
        "type": "product_type",
        "stock_quantity": "stock_available",
    }

    # print("Getting ids")
    # ids = get_ids()
    try:
        with open("id_map.json") as file:
            id_map = json.load(file)
    except FileNotFoundError:
        with open("id_map.json", "w") as file:
            json.dump({}, file)
        id_map = {}

    print("Importing to wordpress")
    processes = {}
    try:
        for i, libro in enumerate(libros):
            if i % SIMULTANEOUS_PROCESSES == 0:
                print(f"Books {i}-{i + SIMULTANEOUS_PROCESSES} / {len(libros)}")
            if str(libro["id"]) in id_map:
                print(f"Updating book {libro['id']} {libro['titleFriendly']}")
                cli = ["wp", f"--path={wordpress_path}", "--user=bob","wc", "product", "update", "--porcelain", id_map[str(libro["id"])]]
            else:
                print(f"Adding book {libro['titleFriendly']}")
                cli = ["wp", f"--path={wordpress_path}", "--user=bob","wc", "product", "create", "--porcelain"]

            for key, value in arg_map.items():
                add_arg(cli, key, libro[value])
            description = libro["book"].get("description", "")
            regular_price = libro["prices"].get("sale", "")
            sale_price = libro["prices"].get("saleSpecialDiscount", "")
            if description is not None:
                add_arg(cli, "description", description)
            if regular_price is not None:
                add_arg(cli, "regular_price", regular_price)
            if sale_price is not None:
                add_arg(cli, "sale_price", sale_price)
            add_arg(cli, "type", "simple")
            original_image_url = libro["mainImg"]
            if original_image_url is not None:
                image_filename = urlsplit(original_image_url).path.lstrip("/")
                add_arg(cli, "images", json.dumps([{"src": f"{wordpress_url}/wp-content/uploads/manual_uploads/{image_filename}"}]))
            add_arg(cli, "attributes", json.dumps([{"name": "original_id", "options": libro["id"]}]))
            processes[str(libro["id"])] = subprocess.Popen(cli, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
            if (i + 1) % SIMULTANEOUS_PROCESSES == 0:
                if not handle_processes(processes, id_map):
                    print("Quitting")
                    break
                processes = {}
    except KeyboardInterrupt:
        handle_processes(processes, id_map)

if __name__ == "__main__":
    
    wordpress_url = os.getenv('wordpress_url')
    wordpress_path = os.getenv('wordpress_path')

    # if len(sys.argv) < 2:
    #     wordpress_url = "http://localhost"
    # else:
    #     wordpress_url = sys.argv[1]
    #     if len(sys.argv) < 3:
    #         wordpress_path = "."
    #     else:
    #         wordpress_path = sys.argv[2]
    
    import_to_wordpress(wordpress_url, wordpress_path)
