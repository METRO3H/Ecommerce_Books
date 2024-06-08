import json

with open("libros-old.json") as file:
    libros_old = json.load(file)

with open("libros.json") as file:
    libros = json.load(file)

libros_old_by_id = {libro["id"]: libro for libro in libros}
libros_by_id = {libro["id"]: libro for libro in libros}
comparison = []
for id in set(libros_old_by_id) | set(libros_by_id):
    if id in libros_old_by_id:
        libro = libros_old_by_id[id]
        stock1 = libro["stock_available"]
        if libro["id"] in libros_by_id:
            stock2 = libros_by_id[libro["id"]]["stock_available"]
        else:
            stock2 = 0
    else:
        libro = libros_by_id[id]
        stock2 = libro["stock_available"]
        if libro["id"] in libros_old_by_id:
            stock2 = libros_by_id[libro["id"]]["stock_available"]
        else:
            stock2 = 0
    ean = libro["ean"]
    title = libro["titleFriendly"]
    difference = stock2 - stock1
    type = libro["product_type"]
    if type in ["book", "ebook"] and (stock1 or stock2):
        comparison.append({
            "id": id,
            "title": title,
            "stock1": stock1,
            "stock2": stock2,
            "difference": difference,
            "type": type,
            "ean": ean,
        })
print(json.dumps(comparison))
