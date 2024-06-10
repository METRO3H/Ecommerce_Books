
import json
import os
def Get_Images():
    none_counter = 0
    with open("libros.json") as json_data:
        data = json.load(json_data)

    images = []

    # Iterar sobre cada item en tus datos
    for item in data:
        # Verificar si 'mainImg' está presente en el item
        if 'mainImg' in item and item["product_type"] == "book" and item["stock_available"]:
            
            image_url = item['mainImg']
            book_name = item["titleFriendly"]
            product_id = item["id"]
            
            if image_url is None:
                #print(product_id, " - ", book_name, " - ", image_url)
                none_counter += 1
                continue
            

            images.append({
                "book_name" : book_name,
                "file_name" : image_url.split("/")[-1],
                "URL" : image_url,
                "product_id" : product_id
            })
            
    #print("None : ", none_counter)
    
    return images