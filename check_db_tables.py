import mysql.connector
from dotenv import load_dotenv
import os
import time

def get_table_row_counts(cursor):
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    table_counts = {}
    for table in tables:
        table_name = table[0]
        try:
            cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
            count = cursor.fetchone()
            table_counts[table_name] = count[0]
        except mysql.connector.Error as err:
            print(f"Error al contar filas en la tabla {table_name}: {err}")
    return table_counts

def main():
    load_dotenv()
    # Conectar a la base de datos
    conn = mysql.connector.connect(
        database=os.getenv("DB_NAME"),
        unix_socket=os.getenv("DB_SOCKET"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        raise_on_warnings=True
    )

    # Obtener el estado inicial de las tablas
    cursor = conn.cursor()
    initial_status = get_table_row_counts(cursor)
    # print("Estado inicial de wp_posts:", initial_status.get("wp_posts", "No encontrado"))

    # Esperar a que se ejecute la importación con `wp wc cli`
    input("Ejecuta la importación con `wp wc cli` y luego presiona Enter...")

    # Esperar un poco para asegurar que los cambios se reflejen
    time.sleep(11)

    # Reconectar para asegurar datos actualizados
    conn.close()
    conn = mysql.connector.connect(
        database=os.getenv("DB_NAME"),
        unix_socket=os.getenv("DB_SOCKET"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        raise_on_warnings=True
    )
    cursor = conn.cursor()

    final_status = get_table_row_counts(cursor)

    # Comparar los estados inicial y final
    changes = {}
    unchanged = {}

    all_tables = set(initial_status.keys()).union(set(final_status.keys()))
    for table in all_tables:
        initial_count = initial_status.get(table, None)
        final_count = final_status.get(table, None)
        if initial_count is None:
            unchanged[table] = 'Tabla solo en estado final'
        elif final_count is None:
            unchanged[table] = 'Tabla solo en estado inicial'
        elif final_count != initial_count:
            changes[table] = {
                'initial_count': initial_count,
                'final_count': final_count
            }
        else:
            unchanged[table] = 'No afectada'

    # Mostrar las tablas afectadas
    if changes:
        print("\n---------------- Tablas relacionadas: ----------------\n")
        for table, info in changes.items():
            print(f"Tabla: {table}")
            print(f"  Registros: {info['initial_count']} -> {info['final_count']}")

    # Mostrar las tablas no afectadas
    if unchanged:
        print("\n---------------- Tablas no afectadas: ----------------\n")
        for table, status in unchanged.items():
            print(f"Tabla: {table}")


    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()

# Example
# wp --path=../../test/app/public --user=wom wc product create --name="Composite Veneers. The Direct-Indirect Technique" --slug=composite-veneers-the-direct-indirect-technique --stock_quantity=1 --description='<p>The direct-indirect technique for composite resin veneer fabrication brings together many of the distinct advantages of the direct and indirect techniques. A direct-indirect restoration is one in which the composite resin is sculpted directly on the tooth structure without previous adhesive preparation, light activated, removed from the tooth, heat tempered, finished and polished extraorally, and finally adhered indirectly in the mouth in a single appointment. The resulting restoration exhibits improved mechanical properties, excellent esthetics, and unrivaled marginal adaptation and polishing. One of the most significant advantages of this technique is the possibility to modulate the final color of the restoration with luting agents, allowing for minor modifications in the restoration hue, chroma, and value. Furthermore, the direct-indirect technique has a wide range of applications, including prepless contact lenses and veneers, veneers with preparation (discolored teeth), fragments, diastema closure, and noncarious cervical lesions, among others. This book systematically covers these many applications and provides step-by-step protocols with specific layering strategies for each. Fifteen detailed case studies are included to showcase the technique in various clinical scenarios, highlighting the materials used and the type of composite veneer selected in each situation. Written by world-renowned masters in their field, this book will surely help to elevate your esthetic outcomes.</p>' --regular_price=218 --type=simple --images="[{"src": "http://localhost:10008/wp-content/uploads/manual_uploads/9780867159592-ca71fbab229eb6a03840d0d59a40129a.jpg"}]" --categories="[{"id": "10597"}]" --tags="[{"id": "11338"}, {"id": "11258"}]" --meta_data="[{"key": "_author", "value": '[\"Fahl Jr., N.\", \"Ritter, A.\"]'}, {"key": "_ean", "value": "9780867159592"}]" --porcelain

