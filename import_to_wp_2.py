# Uso: python import_to_wp.py <URL de wordpress>
# Lee libros.json y llama wp-cli para agregar todos los libros
# Asume <URL de wordpress>/wp-content/uploads/manual_uploads/{image_filename} como ruta de imagen
# Fallará si no se puede abrir la ruta via request (i.e. si <URL de wordpress> está mal)

import json
import subprocess
from urllib.parse import urlsplit
import os
from database import wp_database
from dotenv import load_dotenv
from util.verbose_timer import verbose_time
from util.process_stats import process_stats
import re
import time

def add_arg(cli: list[str], key: str, value: str) -> None:
    cli.append(f"--{key}={value}")
    
    # full_command = " ".join(cli)
    # print(full_command)
    
def add_metadata_arg(metadata_list, key, value):
    metadata_list.append({"key": key, "value": value})
    
def execute_command(cli):
    try:
        process = subprocess.Popen(cli, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        process.wait()
        
        if process.returncode != 0:
            wp_error = process.stderr.read().decode()
            print(wp_error)
            return [False, wp_error]

        return [True, "Success!"]   
            
    except Exception as Error:
        print(Error)
        return [False, Error]

def normalize_string(string_arg):
    
    # Eliminar saltos de línea y tabs
    cleaned_string= re.sub(r'[\n\t\r]+', ' ', string_arg)
    # Reemplazar múltiples espacios por un solo espacio
    cleaned_string = re.sub(r'\s+', ' ', cleaned_string)
    # Eliminar espacios al principio y al final del string
    cleaned_string = cleaned_string.strip()
    
    return cleaned_string

def import_categories(base_command, categories, db_categories_map):

    missing_categories = {category for category in categories if category not in db_categories_map}
    print("-------------------------- Checking Categories --------------------------")
    
    if not missing_categories:
        print("All Expected Categories Found!")
        return
        
    missing_categories_length = len(missing_categories) 
    
    for i, category in enumerate(missing_categories, start=1):
        
        cli = base_command + ["wc", "product_cat", "create", "--porcelain"]
        
        add_arg(cli, "name", category)
        
        [status, message] = execute_command(cli)
        
        percentage = round((i / missing_categories_length)*100, 3)
        
        if status is False:
            print(f"Category {process_stats(i, missing_categories_length)} ERROR Adding : '{category}'")
            print("  ", message)
            continue
        
        
        print(f"Category {process_stats(i, missing_categories_length)} Added : '{category}'")
        
    return
        
def import_tags(base_command, db_tag_map, libros):
    
    scrap_tags = set()
    
    for libro in libros:
        tags = libro.get("themes_text")
        
        for tag in tags:
            scrap_tags.add(normalize_string(tag))
            
    
    missing_tags = {tag for tag in scrap_tags if tag not in db_tag_map}
    
    print("-------------------------- Checking Tags --------------------------")
    
    if not missing_tags:
        print("All Expected Tags Found!")
        return
        
    missing_tags_length = len(missing_tags)
    
    for i, tag in enumerate(missing_tags, 1):
               
        cli = base_command + ["wc", "product_tag", "create", "--porcelain"]
        
        
        add_arg(cli, "name", tag)
        
        [status, message] = execute_command(cli)
        
        if status is False:
            print(f"Tag {process_stats(i, missing_tags_length)} ERROR Adding :")
            print(f"'{tag}'")
            print("  ", message)
            continue
            
        print(f"Tag {process_stats(i, missing_tags_length)} Added : '{tag}'")
        
    return


    # print("len db_tag_map : ", len(db_tag_map))
    # print("-----------------------------------------------------------")
    # print("len scrap_tags : ", len(scrap_tags))
    # print("-----------------------------------------------------------")
    # print("len missing_tags : ", len(missing_tags))
    
def import_products(base_command, libros, db_categories_map, db_tag_map, db_product_map, categories_dic_map, wordpress_url):

    libros_length = len(libros)
    
    print("-------------------------- Importing/Updating Products --------------------------")
    
    for i, libro in enumerate(libros, start=1):

        product_ean = libro["ean"]
        product_name = libro["title"]
        
        product_key = (product_ean, product_name)
        product_id = db_product_map.get(product_key)
        
        cli = base_command + ["wc", "product"]
        
        if product_id:
            cli.extend(["update", str(product_id)]); action = "Updated"
            
        else:
            cli.append("create"); action = "Created"
        
        add_arg(cli, "name", product_name)
        add_arg(cli, "slug", libro["titleFriendly"])
        add_arg(cli, "stock_quantity", libro["stock_available"])
        
        description = f"'{libro['book'].get('description', '')}'"
        regular_price = libro["prices"].get("sale", "")
        sale_price = libro["prices"].get("saleSpecialDiscount", "")
        
        if description:
            add_arg(cli, "description", description)
        if regular_price:
            add_arg(cli, "regular_price", regular_price)
        if sale_price:
            add_arg(cli, "sale_price", sale_price)
            
        add_arg(cli, "type", "simple")
        
        original_image_url = libro["mainImg"]
        
        if original_image_url is not None:
            
            image_filename = urlsplit(original_image_url).path.lstrip("/")
            image_path = f"{wordpress_url}/wp-content/uploads/manual_uploads/{image_filename}"
            image_param = json.dumps([{'src': image_path}])
            add_arg(cli, "images", image_param)
        
        
        product_category = libro.get("product_type")
        
        if product_category:
            
            category_dic = categories_dic_map.get(product_category)
            category_id = db_categories_map.get(category_dic)
            category_param = json.dumps([{'id': str(category_id)}])
            add_arg(cli, "categories", category_param)
        
        product_tags = libro.get("themes_text")
        
        if product_tags:
            tags_param = [{'id': str(db_tag_map[normalize_string(tag)])} for tag in product_tags]
            tags_param = json.dumps(tags_param)
        
            add_arg(cli, "tags", tags_param)
            
            
        metadata_list = []
        authors_list = [author.get("name") for author in libro["book"].get("authors")]
        authors_list = json.dumps(authors_list)
        
        add_metadata_arg(metadata_list, "_author", authors_list)
        
        add_metadata_arg(metadata_list, "_ean", product_ean)
        
        metadata_list = json.dumps(metadata_list)
        
        add_arg(cli, "meta_data", metadata_list)
        
        cli.append("--porcelain")
        
        # full_command = " ".join(cli)
        # print(full_command)
        
        [status, message] = execute_command(cli)
                
        if status is False:
            action = "ERROR"
            continue
        
        product_name = product_name[:90] + "..." if len(product_name) > 90 else product_name
        
        print(f"Book {process_stats(i, libros_length)} - {action} : ({product_ean}, {product_name})")  
        if status is False:
            print("  ", message)   
        
def import_to_wordpress(wordpress_url, wordpress_path, wordpress_user):
    
    base_command = ["wp", f"--path={wordpress_path}", f"--user={wordpress_user}"]
    
    
    print("Loading libros.json")
    with open("libros.json") as file:
        libros = json.load(file)

    libros = [libro for libro in libros if libro["product_type"] == "book" and libro["stock_available"]]
    
    db = wp_database()
    db.connect()
    
    db_categories_map = db.get_all_categories(name_map = True)
    db_tag_map = db.get_all_tags(name_map = True)

    db.close()
    
    categories = ["Libros", "E-Books"]
    
    import_categories(base_command, categories, db_categories_map)
    
    start_tag_import = time.time()
    
    import_tags(base_command, db_tag_map, libros)
    
    end_tag_import = time.time()
    
    tag_import_time = end_tag_import - start_tag_import
    print("\nTag importation : ", verbose_time(tag_import_time), "\n")
    
    db.connect()
    db_categories_map = db.get_all_categories(name_map = True)
    db_tag_map = db.get_all_tags(name_map = True)
    db_product_map = db.get_all_products(unique_key_map = True)
    db.close()
    
    start_product_import = time.time()
    
    categories_dic_map = {
        "book": categories[0],
        "ebook": categories[1]
    }   
    import_products(base_command, libros, db_categories_map, db_tag_map, db_product_map, categories_dic_map, wordpress_url)
    
    end_product_import = time.time()
    
    product_import_time = end_product_import - start_product_import
    print("\nProduct importation : ", verbose_time(product_import_time), "\n")

if __name__ == "__main__":
    load_dotenv()
    wordpress_url = os.getenv("WORDPRESS_URL")
    wordpress_path = os.getenv("WORDPRESS_PATH")
    wordpress_user = os.getenv("WORDPRESS_USER")

    import_to_wordpress(wordpress_url, wordpress_path, wordpress_user)
