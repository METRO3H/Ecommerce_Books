
import sqlite3

def filter_images(images):
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    query = """
    --sql
    SELECT book_name, file_name, url, product_id FROM covers
    ;
    """
    cursor.execute(query)
    saved_images = cursor.fetchall()

    conn.close()

    columns = [description[0] for description in cursor.description]

    saved_images_dictionary = []

    for saved_image in saved_images:
        dict_row = dict(zip(columns, saved_image))
        saved_images_dictionary.append(dict_row)

    # for i in range(10):
    #     print("Images : ", json.dumps(images[i], indent=2))
    #     print("Saved images : ", json.dumps(saved_images_dictionary[i], indent=2))

    # missing_images = [item for item in images if item not in saved_images_dictionary]

    saved_product_ids = {item['product_id'] for item in saved_images_dictionary}

    missing_images  = [item for item in images if item['product_id'] not in saved_product_ids]

    return missing_images