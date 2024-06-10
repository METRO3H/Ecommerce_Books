# Modo de operación
## 1. fetch_graphql.py
Scrapea todos los productos de axon y los pone en libros.json

## 2. download_images.py
1. Obtiene las URL posibles a partir de libros.json pero descarta los obtenidos de descargados.db
2. Descarga asincrónicamente a una carpeta downloads/ en cualquier parte
3. Corre wp media import downloads/*
4. Agrega las URL de las imágenes trabajadas a descargados.db
5. Elimina todo dentro de downloads/

## 3. import_to_wordpress.py
Aún no definido, investigando CLI de Woocommerce
