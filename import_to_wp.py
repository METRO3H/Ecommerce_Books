# Uso: python import_to_wp.py <URL de wordpress>
# Lee libros.json y llama wp-cli para agregar todos los libros
# Asume <URL de wordpress>/wp-content/uploads/manual_uploads/{image_filename} como ruta de imagen
# Fallará si no se puede abrir la ruta via request (i.e. si <URL de wordpress> está mal)

import json
import subprocess
from urllib.parse import urlsplit
import itertools
import sys
import os
from dotenv import load_dotenv

SIMULTANEOUS_PROCESSES = 10

def add_arg(cli: list[str], key: str, value: str) -> None:
    cli.append(f"--{key}={value}")

def handle_product_processes(processes, id_map) -> bool:
    success = True
    for id, process in processes.items():
        if process.wait():
            success = False
        output = process.stdout.read().decode()
        if output:
            id_map[str(id)] = output.strip()
            with open("id_map.json", "w") as file:
                json.dump(id_map, file)
    return success

def handle_tag_processes(processes, tag_map) -> bool:
    success = True
    for tag_id, process in processes.items():
        if process.wait():
            success = False
        output = process.stdout.read().decode()
        if output:
            tag_map[str(tag_id)] = output.strip()
            with open("tag_map.json", "w") as file:
                json.dump(tag_map, file)
    return success

def import_to_wordpress(wordpress_url, wordpress_path, wordpress_user):
    print("Loading libros.json")
    with open("libros.json") as file:
        libros = json.load(file)

    # libros = [libro for libro in libros if libro["product_type"] == "book" and libro["stock_available"]]

    arg_map = {
        "name": "title",
        "slug": "titleFriendly",
        "type": "product_type",
        "stock_quantity": "stock_available",
    }

    try:
        with open("id_map.json") as file:
            id_map = json.load(file)
    except FileNotFoundError:
        with open("id_map.json", "w") as file:
            json.dump({}, file)
        id_map = {}

    try:
        with open("tag_map.json") as file:
            tag_map = json.load(file)
    except FileNotFoundError:
        with open("tag_map.json", "w") as file:
            json.dump({}, file)
        tag_map = {}

    print("Importing to wordpress")
    try:
        processes = {}
        print("Importing tags")
        for i, libro in enumerate(libros):
            if not libro.get("themes"):
                continue
            if i % SIMULTANEOUS_PROCESSES == 0:
                print(f"Tags of books {i}-{i + SIMULTANEOUS_PROCESSES - 1} / {len(libros)}")
            for tag_id, tag_name in zip(libro["themes"], libro["themes_text"]):
                if str(tag_id) in tag_map:
                    continue
                print(f"Adding tag '{tag_name}'")
                cli = ["wp", f"--path={wordpress_path}", f"--user={wordpress_user}", "wc", "product_tag", "create", "--porcelain"]
                add_arg(cli, "name", tag_name)

                processes[str(tag_id)] = subprocess.Popen(cli, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if (i + 1) % SIMULTANEOUS_PROCESSES == 0:
                    if not handle_tag_processes(processes, tag_map):
                        print("Quitting")
                        break
                    processes = {}
        handle_tag_processes(processes, tag_map)
    except KeyboardInterrupt:
        handle_tag_processes(processes, tag_map)

    try:
        processes = {}
        print("Importing products")
        for i, libro in enumerate(libros):
            if i % SIMULTANEOUS_PROCESSES == 0:
                print(f"Books {i}-{i + SIMULTANEOUS_PROCESSES - 1} / {len(libros)}")
            if str(libro["id"]) in id_map:
                print(f"Updating book {libro['id']} {libro['titleFriendly']}")
                cli = ["wp", f"--path={wordpress_path}", f"--user={wordpress_user}", "wc", "product", "update", "--porcelain", id_map[str(libro["id"])]]
            else:
                print(f"Adding book {libro['titleFriendly']}")
                cli = ["wp", f"--path={wordpress_path}", f"--user={wordpress_user}", "wc", "product", "create", "--porcelain"]

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
            if libro.get("themes"):
                add_arg(cli, "tags", json.dumps([{"id": tag_map[str(tag_id)]} for tag_id in libro["themes"]]))

            processes[str(libro["id"])] = subprocess.Popen(cli, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if (i + 1) % SIMULTANEOUS_PROCESSES == 0:
                if not handle_product_processes(processes, id_map):
                    print("Quitting")
                    break
                processes = {}
        handle_product_processes(processes, id_map)
    except KeyboardInterrupt:
        handle_product_processes(processes, id_map)

if __name__ == "__main__":
    load_dotenv()
    wordpress_url = os.getenv("WORDPRESS_URL")
    wordpress_path = os.getenv("WORDPRESS_PATH")
    wordpress_user = os.getenv("WORDPRESS_USER")

    import_to_wordpress(wordpress_url, wordpress_path, wordpress_user)
