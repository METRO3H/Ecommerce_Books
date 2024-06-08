import requests
import json
import os

def Download_Image(url, output_folder):
    image_name = url.split('/')[-1]  # Obtiene el nombre del archivo de la URL
    image_path = os.path.join(output_folder, image_name)  # Crea la ruta completa del archivo
    
    if os.path.exists(image_path):
        return
        
    # Realiza la solicitud HTTP
    respond = requests.get(url)
    if respond.status_code == 200:
        content = respond.content
        
        if content is None:
            return

        with open(image_path, 'wb') as file:
            file.write(content)
        print(f'Imagen descargada correctamente: {image_path}')
    else:
        print(f'Error al descargar la imagen: {respond.status_code}')

    return


def Get_Images():
    none_counter = 0
    with open('libros.json') as json_data:
        data = json.load(json_data)

    URL_Images = []

    # Iterar sobre cada item en tus datos
    for item in data:
        # Verificar si 'mainImg' está presente en el item
        if 'mainImg' in item and item["product_type"] == "book" and item["stock_available"]:
            
            image_url = item['mainImg']
            
            if image_url is None:
                print(item["id"]," - ",item["titleFriendly"], " - ", image_url)
                none_counter += 1
                continue
            

            URL_Images.append(image_url)
    print("None : ", none_counter)
    return URL_Images



URL_Images = Get_Images()

print(len(URL_Images))
