import json
import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import html

class wp_database:
    def __init__(self):
        load_dotenv()
        self.config = {
            'database': os.getenv("DB_NAME"),
            'unix_socket': os.getenv("DB_SOCKET"),
            'user': os.getenv("DB_USER"),
            'password': os.getenv("DB_PASSWORD"),
            'raise_on_warnings': True
        }
        self.connection = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.config)
            # if self.connection.is_connected():
            #     print('Conexión establecida a la base de datos MySQL')
        except Error as e:
            print(f'Error al conectar a MySQL: {e}')

    def execute_fetch_all(self, query, dictionary = False):
        try:
            if self.connection is None or not self.connection.is_connected():
                self.connect()
            cursor = self.connection.cursor(dictionary=dictionary)
            cursor.execute(query)
            result = cursor.fetchall()

            return result
        
        except Error:
            print(f'Error al ejecutar la consulta: {Error}')
            return None
        finally:
            if cursor:
                cursor.close()
                
    def get_all_tags(self, name_map = False, dictionary = False):
        
        query = """-- sql
            SELECT wp_terms.name, wp_terms.term_id
            FROM wp_terms 
            JOIN wp_term_taxonomy ON wp_term_taxonomy.term_id = wp_terms.term_id 
            WHERE wp_term_taxonomy.taxonomy = 'product_tag'
        ;
        """
         
        result = self.execute_fetch_all(query, dictionary)
        
        if name_map:
            result = {html.unescape(item[0]): item[1] for item in result}
                
        return result
    
    def get_all_categories(self, name_map = False, dictionary = False):
        
        query = """-- sql
            SELECT wp_terms.name, wp_term_taxonomy.term_id FROM `wp_term_taxonomy`
            JOIN wp_terms ON wp_terms.term_id = wp_term_taxonomy.term_id
            WHERE wp_term_taxonomy.taxonomy = 'product_cat'
        ;
        """
    
        result = self.execute_fetch_all(query, dictionary)
        
        if name_map:
            result = {html.unescape(item[0]): item[1] for item in result}
                
        return result
    
    def get_all_products(self, unique_key_map=False):
    
        query = """-- sql
            SELECT ID, post_title, meta_key, meta_value AS "ean" FROM `wp_posts` 
            JOIN wp_postmeta ON wp_postmeta.post_id = wp_posts.ID
            WHERE `post_type` = 'product' 
            AND wp_postmeta.meta_key = "_ean"
        ;
        """
        result = self.execute_fetch_all(query, dictionary = True) 
        
        if unique_key_map:
            tuple_map = {}
            for product in result:
                key = (product["ean"], html.unescape(product["post_title"]))
                value = product["ID"] 
                
                tuple_map[key] = value
                
            result = tuple_map
        
        return result
    
    
    def close(self):
        if self.connection is not None and self.connection.is_connected():
            self.connection.close()
            # print('Conexión cerrada.')


if __name__ == "__main__":
    db = wp_database()
    
    query = """-- sql
    SELECT wp_terms.name, wp_terms.term_id
    FROM wp_terms 
    JOIN wp_term_taxonomy ON wp_term_taxonomy.term_id = wp_terms.term_id 
    WHERE wp_term_taxonomy.taxonomy = 'product_tag'
    ;
    """
    result = db.execute_fetch_all(query, dictionary=True)
    if result:
        print(result)
        
    db.close()
