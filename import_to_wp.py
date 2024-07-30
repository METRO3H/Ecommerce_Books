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

def add_arg(cli: list[str], key: str, value: str) -> None:
    cli.append(f"--{key}={value}")
    
    # full_command = " ".join(cli)
    # print(full_command)

def import_categories(wordpress_path, wordpress_user):
    
    categories = ["Libros", "E-Books"]
    
    for category in categories:
        
        print(f"Adding category '{category}'")
        
        cli = ["wp", f"--path={wordpress_path}", f"--user={wordpress_user}", "wc", "product_cat", "create", "--porcelain"]
        
        add_arg(cli, "name", category)
        
        process = subprocess.Popen(cli, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        process.wait()
        
        if process.returncode != 0:
            error = process.stderr.read()
            print(error.decode())
            continue

        

def import_to_wordpress(wordpress_url, wordpress_path, wordpress_user):
    print("Loading libros.json")
    with open("libros.json") as file:
        libros = json.load(file)

    libros = [libro for libro in libros if libro["product_type"] == "book" and libro["stock_available"]]

    arg_map = {
        "name": "title",
        "slug": "titleFriendly",
        #"type": "product_type",
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
        print("Importing categories")
        import_categories(wordpress_path, wordpress_user)
        
        
        print("Importing tags")
        quitting = False
        for i, libro in enumerate(libros, 1):

            if not libro.get("themes"):
                continue
            libros_length = len(libros)
            percentage = round((i / libros_length)*100, 3)
            print(f"Tags of book {i}/{libros_length} - {percentage}%")
            for tag_id, tag_name in zip(libro["themes"], libro["themes_text"]):
                if str(tag_id) in tag_map:
                    continue
                print(f"Adding tag '{tag_name}'")
                
                cli = ["wp", f"--path={wordpress_path}", f"--user={wordpress_user}", "wc", "product_tag", "create", "--porcelain"]
                
                
                add_arg(cli, "name", tag_name)
                
                process = subprocess.Popen(cli, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

                process.wait()
                
                if process.returncode != 0:
                    error = process.stderr.read()
                    print(error.decode())
                    continue
                    # quitting = True
                    # break
                    
                output = process.stdout.read().decode()
                
                if output:
                    tag_map[str(tag_id)] = output.strip()
                    with open("tag_map.json", "w") as file:
                        json.dump(tag_map, file)
            if quitting:
                break
    except KeyboardInterrupt:
        pass

    try:
        print("\nImporting products\n")
        for i, libro in enumerate(libros, 1):
            libros_length = len(libros)
            percentage = round((i/libros_length)*100, 3)
            print(f"Book {i}/{libros_length} - {percentage}%")
            if str(libro["id"]) in id_map:
                print(f"Updating book {libro['id']} {libro['titleFriendly']}")
                cli = ["wp", f"--path={wordpress_path}", f"--user={wordpress_user}", "wc", "product", "update", "--porcelain", id_map[str(libro["id"])]]
            else:
                print(f"Adding book {libro['titleFriendly']}")
                cli = ["wp", f"--path={wordpress_path}", f"--user={wordpress_user}", "wc", "product", "create", "--porcelain"]
            
            
            for key, value in arg_map.items():
                libro_value = libro[value]
                
                # if key != "stock_quantity":
                #     libro_value = f"'{libro_value}'"
                
                add_arg(cli, key, libro_value)


            description = f"'{libro['book'].get('description', '')}'"
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
                image_path = f"{wordpress_url}/wp-content/uploads/manual_uploads/{image_filename}"
                image_param = json.dumps([{'src': image_path}])
                add_arg(cli, "images", image_param)
            
            #arreglo a la mala por mientras XD
            categories_map = {
                "book": 4466,
                "ebook": 4467
            }
            
            if libro.get("product_type"):
                category_param = json.dumps([{'id': categories_map.get(libro["product_type"])}])
                add_arg(cli, "categories", category_param)
                
            
            
            
            if libro.get("themes"):
                tags_param = json.dumps([{'id': tag_map[str(tag_id)]} for tag_id in libro['themes']])
                # tags_param = json.dumps([{'id': 2408}])
                add_arg(cli, "tags", tags_param)
            
            # full_command = " ".join(cli)
            # print(full_command)
            
            process = subprocess.Popen(cli, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            process.wait()
            
            if process.returncode != 0:
                error = process.stderr.read()
                print(error.decode())
                break
            output = process.stdout.read().decode()
            if output:
                id_map[str(id)] = output.strip()
                with open("id_map.json", "w") as file:
                    json.dump(id_map, file)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    load_dotenv()
    wordpress_url = os.getenv("WORDPRESS_URL")
    wordpress_path = os.getenv("WORDPRESS_PATH")
    wordpress_user = os.getenv("WORDPRESS_USER")

    import_to_wordpress(wordpress_url, wordpress_path, wordpress_user)
