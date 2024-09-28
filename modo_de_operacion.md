# Modo de operación
## 1. `scraping/scrape.py`
Scrapea todos los productos de axon y los pone en libros.json

## 2. `main.py`
1. Obtiene las URL posibles a partir de libros.json pero descarta las que ya se tienen descargadas (están en database/database.db)
2. Descarga asincrónicamente a la carpeta images/
3. Agrega las URL de las imágenes descargadas a database/database.db

## 3. ???
1. Corre wp media import images/* ??
2. Elimina todo dentro de downloads/ ?

## 4. `import_to_wp_2.py`
1. Agrega categorías de los productos con `wp-cli` si es que no existen ya en MySQL
2. Agrega tags de los productos con `wp-cli` si es que no existen ya en MySQL
3. Agrega/actualiza todos los productos con `wp-cli`
