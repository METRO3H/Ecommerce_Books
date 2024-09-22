
import sqlite3

def insert_images(images):
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    query = """
    --sql
    INSERT INTO covers (book_name, file_name, url, product_id)
    VALUES (?, ?, ?, ?)
    ;
    """
    total_rows_inserted = 0
    for image in images:

        book_name = image["book_name"]
        file_name = image["file_name"]
        URL = image['URL']
        product_id = image["product_id"]

        cursor.execute(query, (book_name, file_name, URL, product_id,))

        total_rows_inserted += cursor.rowcount

    conn.commit()
    conn.close()

    return total_rows_inserted