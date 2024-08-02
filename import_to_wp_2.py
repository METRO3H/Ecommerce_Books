# Uso: python import_to_wp.py <URL de wordpress>
# Lee libros.json y llama wp-cli para agregar todos los libros
# Asume <URL de wordpress>/wp-content/uploads/manual_uploads/{image_filename} como ruta de imagen
# Fallará si no se puede abrir la ruta via request (i.e. si <URL de wordpress> está mal)

import json
import subprocess
from urllib.parse import urlsplit
import os
from database import Database
from dotenv import load_dotenv

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
            wp_error = process.stderr.read()
            print(wp_error.decode())
            return False
        
        return True    
            
    except Exception as Error:
        print(Error)
        return False

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
        
        result = execute_command(cli)
        
        percentage = round((i / missing_categories_length)*100, 3)
        
        if result is False:
            print(f"Category {i}/{missing_categories_length} - {percentage}% ERROR Adding : '{category}'")
            continue
        
        
        print(f"Category {i}/{missing_categories_length} - {percentage}% Added : '{category}'")
        
    return
        
def import_tags(base_command, db_tag_map, libros):
    
    scrap_tags = set()
    
    for libro in libros:
        tags = libro.get("themes_text")
        
        for tag in tags:
            scrap_tags.add(tag)
            
    
    missing_tags = {tag for tag in scrap_tags if tag not in db_tag_map}
    
    print("-------------------------- Checking Tags --------------------------")
    
    if not missing_tags:
        print("All Expected Tags Found!")
        return
        
    missing_tags_length = len(missing_tags)
    
    for i, tag in enumerate(missing_tags, 1):
        
        percentage = round((i / missing_tags_length)*100, 3)
       
        
        cli = base_command + ["wc", "product_tag", "create", "--porcelain"]
        
        
        add_arg(cli, "name", tag)
        
        result = execute_command(cli)
        
        if result is False:
            print(f"Tag {i}/{missing_tags_length} - {percentage}% ERROR Adding : '{tag}'")
            continue
            
        print(f"Tag {i}/{missing_tags_length} - {percentage}% Added : '{tag}'")
        
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

        percentage = round((i/libros_length)*100, 3)
        product_ean = libro["ean"]
        product_name = libro["title"]
        
        product_key = (product_ean, product_name)
        product_id = db_product_map.get(product_key)
        
        cli = base_command + ["wc", "product"]
        
        if product_id:
            cli.extend(["update", product_id]); action = "Updated"
            
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
            category_param = json.dumps([{'id': category_id}])
            add_arg(cli, "categories", category_param)
        
        product_tags = libro.get("themes_text")
        
        if product_tags:
            tags_param = [{'id': db_tag_map[tag]} for tag in product_tags]
            tags_param = json.dumps(tags_param)
        
            add_arg(cli, "tags", tags_param)
            
            
        metadata_list = []
        authors_list = [author.get("name") for author in libro["book"].get("authors")]
        authors_list = json.dumps(authors_list)
        
        add_metadata_arg(metadata_list, "_author", authors_list)
        
        add_metadata_arg(metadata_list, "_ean", product_ean)
        
        metadata_list = json.dumps(metadata_list)
        
        add_arg(cli, "--meta_data", metadata_list)
        
        cli.append("--porcelain")

        result = execute_command(cli)
                
        if result is False:
            action = "ERROR"
            continue
        
        product_name = product_name[:10] + "..." if len(product_name) > 10 else ""
        
        print(f"Book {i}/{libros_length} - {percentage}% - {action} : ({product_ean}, {product_name})")       
        
def import_to_wordpress(wordpress_url, wordpress_path, wordpress_user):
    
    base_command = ["wp", f"--path={wordpress_path}", f"--user={wordpress_user}"]
    
    
    print("Loading libros.json")
    with open("libros.json") as file:
        libros = json.load(file)

    libros = [libro for libro in libros if libro["product_type"] == "book" and libro["stock_available"]]
    
    db = Database()
    db.connect()
    
    db_categories_map = db.get_all_categories(name_map = True)
    db_tag_map = db.get_all_tags(name_map = True)

    db.close()
    
    categories = ["Libros", "E-Books"]
    
    import_categories(base_command, categories, db_categories_map)
  
    import_tags(base_command, db_tag_map, libros)
    
    db.connect()
    
    db_categories_map = db.get_all_categories(name_map = True)
    db_tag_map = db.get_all_tags(name_map = True)
    db_product_map = db.get_all_products(unique_key_map = True)
    
    db.close()
    
    categories_dic_map = {
        "book": categories[0],
        "ebook": categories[1]
    }   
    
    import_products(base_command, libros, db_categories_map, db_tag_map, db_product_map, categories_dic_map, wordpress_url)


if __name__ == "__main__":
    load_dotenv()
    wordpress_url = os.getenv("WORDPRESS_URL")
    wordpress_path = os.getenv("WORDPRESS_PATH")
    wordpress_user = os.getenv("WORDPRESS_USER")

    import_to_wordpress(wordpress_url, wordpress_path, wordpress_user)
