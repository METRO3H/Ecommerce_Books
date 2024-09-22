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
from util.color import color, process_print_division
import re
import time

def arg(key: str, value: str) -> str:
    return f"--{key}={value}"

def metadata(key, value):
    return {"key": key, "value": value}

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

    print(color("title_card", " Script "), "Starting the", color("blue","Category"), "import process!")

    start_import = time.time()

    missing_categories = {category for category in categories if category not in db_categories_map}
    print(color("magneta", "[Status] Checking Categories..."))

    if not missing_categories:
        print(color("green", "[Status] All Expected Categories Found!"))
        return

    missing_categories_length = len(missing_categories)
    print()
    for i, category in enumerate(missing_categories, start=1):

        cli = base_command + ["wc", "product_cat", "create", "--porcelain"]

        cli.append(arg("name", category))

        [status, message] = execute_command(cli)

        if not status:
            print(color("red", f"[status] Category {process_stats(i, missing_categories_length)} : '{category}'"))
            print(color("red", f"   --> {message}"))
            continue

        print(color("green","[status]"), f"Category {process_stats(i, missing_categories_length)} : '{category}'")

    end_import = time.time()

    print(color("cyan", f"\n[Status] Process completed in {verbose_time(end_import - start_import)}"))

    return

def import_tags(base_command, db_tag_map, libros):

    print(color("title_card", " Script "), "Starting the", color("blue","Tag"), "import process!")

    start_import = time.time()
    scrap_tags = set()

    for libro in libros:
        tags = libro.get("themes_text")

        for tag in tags:
            scrap_tags.add(normalize_string(tag))


    missing_tags = {tag for tag in scrap_tags if tag not in db_tag_map}

    print(color("magneta", "[Status] Checking Tags..."))
    if not missing_tags:
        print(color("green", "[Status] All Expected Tags Found!"))
        return

    missing_tags_length = len(missing_tags)
    print()
    for i, tag in enumerate(missing_tags, 1):

        cli = base_command + ["wc", "product_tag", "create", "--porcelain"]

        cli.append(arg("name", tag))

        [status, message] = execute_command(cli)

        if not status:
            print(color("red", f"[Status] Tag {process_stats(i, missing_tags_length)} : '{tag}'"))
            print(color("red", f"   --> {message}"))
            continue

        print(color("green", "[Status]"), f"Tag {process_stats(i, missing_tags_length)} : '{tag}'")

    end_import = time.time()

    print(color("cyan", f"\n[Status] Process completed in {verbose_time(end_import - start_import)}"))

    return

def import_products(base_command, libros, db_categories_map, db_tag_map, db_product_map, categories, wordpress_url):

    print(color("title_card", " Script "), "Starting the", color("blue","Product"), "import process!\n")

    start_import = time.time()

    categories_dic_map = {
        "book": categories[0],
        "ebook": categories[1]
    }

    libros_length = len(libros)


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

        cli.append(arg("name", product_name))
        cli.append(arg("slug", libro["titleFriendly"]))
        cli.append(arg("stock_quantity", libro["stock_available"]))

        description = f"'{libro['book'].get('description', '')}'"
        regular_price = libro["prices"].get("sale", "")
        sale_price = libro["prices"].get("saleSpecialDiscount", "")

        if description:
            cli.append(arg("description", description))
        if regular_price:
            cli.append(arg("regular_price", regular_price))
        if sale_price:
            cli.append(arg("sale_price", sale_price))

        cli.append(arg("type", "simple"))

        original_image_url = libro["mainImg"]

        if original_image_url is not None:

            image_filename = urlsplit(original_image_url).path.lstrip("/")
            image_path = f"{wordpress_url}/wp-content/uploads/manual_uploads/{image_filename}"
            image_param = json.dumps([{'src': image_path}])
            cli.append(arg("images", image_param))


        product_category = libro.get("product_type")

        if product_category:

            category_dic = categories_dic_map.get(product_category)
            category_id = db_categories_map.get(category_dic)
            category_param = json.dumps([{'id': str(category_id)}])
            cli.append(arg("categories", category_param))

        product_tags = libro.get("themes_text")

        if product_tags:
            tags_param = [{'id': str(db_tag_map[normalize_string(tag)])} for tag in product_tags]
            tags_param = json.dumps(tags_param)

            cli.append(arg("tags", tags_param))


        metadata_list = []
        authors_list = [author.get("name") for author in libro["book"].get("authors")]
        authors_list = json.dumps(authors_list)

        metadata_list.append(metadata("_author", authors_list))

        metadata_list.append(metadata("_ean", product_ean))

        metadata_list = json.dumps(metadata_list)

        cli.append(arg("meta_data", metadata_list))

        cli.append("--porcelain")

        [status, message] = execute_command(cli)

        if status is False:
            print(color("red", f"[Status] Book {process_stats(i, libros_length)} - {action} - ERROR : ({product_ean}, {product_name})"))
            print(color("red", f"   --> {message}"))
            continue

        product_name = product_name[:70] + "..." if len(product_name) > 70 else product_name

        print(color("green", "[Status]"), f"Book {process_stats(i, libros_length)} - {action} : ({product_ean}, {product_name})")


    end_import = time.time()

    print(color("cyan", f"[Status] Process completed in {verbose_time(end_import - start_import)}"))

def import_to_wordpress(wordpress_url, wordpress_path, wordpress_user):

    base_command = ["wp", f"--path={wordpress_path}", f"--user={wordpress_user}"]

    process_print_division()
    print(color("title_card", " Script "), "Starting", color("blue","Woocommerce"), "update process!")
    process_print_division()

    print(color("title_card", " Script "), "Starting the", color("blue","Data"), "collection process!")

    with open("libros.json") as file:
        libros = json.load(file)
    if not libros:
        print(color("red","[Status]"), color("blue", "Scraped data"),"is empty!")
        return

    libros = [libro for libro in libros if libro["product_type"] == "book" and libro["stock_available"] > 2 ]

    if libros:
        print(color("green","[Status]"), color("blue", "Scraped data"),"successfully extracted!")

    db = wp_database()
    db.connect()

    db_categories_map = db.get_all_categories(name_map = True)
    db_tag_map = db.get_all_tags(name_map = True)

    db.close()

    print(color("green","[Status]"),"WP database", color("blue", "Categories"), "successfully extracted!")
    print(color("green","[Status]"),"WP database", color("blue", "Tags"), "successfully extracted!")

    process_print_division()

    categories = ["Libros", "E-Books"]

    import_categories(base_command, categories, db_categories_map)

    process_print_division()

    import_tags(base_command, db_tag_map, libros)

    process_print_division()

    print(color("title_card", " Script "), "Restarting the", color("blue","Data"), "collection process!")

    db.connect()
    db_categories_map = db.get_all_categories(name_map = True)
    db_tag_map = db.get_all_tags(name_map = True)
    db_product_map = db.get_all_products(unique_key_map = True)
    db.close()

    if (not db_categories_map) or (not db_tag_map):
        print(color("red","[Status]"),"WP database", color("blue", "Categories"), "or", color("blue", "Tags"), "are empty!")
        print(color("red", f"   --> WP database categories length: {len(db_categories_map)}"))
        print(color("red", f"   --> WP database tags length: {len(db_tag_map)}"))
        return


    print(color("green","[Status]"),"WP database", color("blue", "Categories"), "successfully extracted!")

    print(color("green","[Status]"),"WP database", color("blue", "Tags"), "successfully extracted!")

    print(color("green","[Status]"),"WP database", color("blue", "Products"), "successfully extracted!")

    process_print_division()

    import_products(base_command, libros, db_categories_map, db_tag_map, db_product_map, categories, wordpress_url)

    process_print_division()


if __name__ == "__main__":

    start_time = time.time()

    load_dotenv()
    wordpress_url = os.getenv("WORDPRESS_URL")
    wordpress_path = os.getenv("WORDPRESS_PATH")
    wordpress_user = os.getenv("WORDPRESS_USER")

    import_to_wordpress(wordpress_url, wordpress_path, wordpress_user)

    end_time = time.time()

    print(color("cyan", f"[Status] Process completed in {verbose_time(end_time - start_time)}"))
