import os

# Lista de IDs de libros
book_ids = ['123', '456', '789']  # Ejemplo de IDs, reemplaza con tus datos

# Directorio de imágenes
image_directory = '/images/'

# Obtener lista de archivos en el directorio de imágenes
image_files = os.listdir(image_directory)

# Filtrar imágenes que no están en la lista de IDs de libros
for image_file in image_files:
    # Extraer el ID del nombre del archivo
    image_id = os.path.splitext(image_file)[0]

    # Si el ID no está en la lista de IDs de libros, eliminar el archivo
    if image_id not in book_ids:
        file_path = os.path.join(image_directory, image_file)
        os.remove(file_path)
        print(f'Eliminado: {file_path}')
