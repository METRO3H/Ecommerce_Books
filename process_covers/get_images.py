
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
        if 'mainImg' in item:

            image_url = item['mainImg']
            book_name = item["titleFriendly"]
            product_id = item["id"]


            if image_url is None:
                #print(product_id, " - ", book_name, " - ", image_url)
                none_counter += 1
                continue

            file_name = image_url.split("/")[-1]
            if str(product_id) == str(141208):
                print(product_id)
                print(image_url)
                print(file_name)


            images.append({
                "book_name" : book_name,
                "file_name" : file_name,
                "URL" : image_url,
                "product_id" : product_id
            })

    #print("None : ", none_counter)
<<<<<<< HEAD
    
    return images
=======

    return images
>>>>>>> cab7421 (cleanup: Remove lines with only whitespace)
