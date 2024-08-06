import mysql.connector
from dotenv import load_dotenv
import os
def get_table_status(cursor):
    cursor.execute("SHOW TABLE STATUS")
    return {row['Name']: (row['Rows'], row['Data_length']) for row in cursor.fetchall()}

def main():
    load_dotenv()
    # Conectar a la base de datos
    conn = mysql.connector.connect(
        database = os.getenv("DB_NAME"),
        unix_socket = os.getenv("DB_SOCKET"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        raise_on_warnings = True
    )
    cursor = conn.cursor(dictionary=True)

    # Obtener el estado inicial de las tablas
    initial_status = get_table_status(cursor)

    # Esperar a que se ejecute la importación con `wp wc cli`
    input("Ejecuta la importación con `wp wc cli` y luego presiona Enter...")

    # Obtener el estado final de las tablas
    final_status = get_table_status(cursor)

    # Comparar los estados inicial y final
    changes = {}
    for table, (initial_rows, initial_size) in initial_status.items():
        final_rows, final_size = final_status.get(table, (None, None))
        if final_rows != initial_rows or final_size != initial_size:
            changes[table] = {
                'initial_rows': initial_rows,
                'final_rows': final_rows,
                'initial_size': initial_size,
                'final_size': final_size
            }

    # Mostrar las tablas afectadas
    if changes:
        print("Tablas afectadas:")
        for table, info in changes.items():
            print(f"Tabla: {table}")
            print(f"  Registros: {info['initial_rows']} -> {info['final_rows']}")
            print(f"  Tamaño: {info['initial_size']} -> {info['final_size']}")
    else:
        print("No se detectaron cambios en las tablas.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
