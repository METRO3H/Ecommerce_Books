
import json
import os
import asyncio
import aiohttp
import aiofiles

async def Download_Image(url, output_folder, session):
    image_name = url.split('/')[-1]  # Obtiene el nombre del archivo de la URL
    image_path = os.path.join(output_folder, image_name)  # Crea la ruta completa del archivo
    
    if os.path.exists(image_path):
        return
        

    
    async with session.get(url) as response:
        
        if response.status == 200:
            content = await response.read()
            if content is None:
                return
            async with aiofiles.open(image_path, mode="wb") as file:
                await file.write(content)

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

def remove_images(URL_Images):
    # Obtener lista de archivos en el directorio de imágenes
    image_files = os.listdir(output_folder)
    
    # Filtrar imágenes que no están en la lista de IDs de libros
    for image_file in image_files:
        # Extraer el ID del nombre del archivo
        image_id = os.path.splitext(image_file)[0]

        # Si el ID no está en la lista de IDs de libros, eliminar el archivo
        if image_id not in URL_Images:
            file_path = os.path.join(output_folder, image_file)
            os.remove(file_path)
            print(f'Eliminado: {file_path}')
            
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    return

output_folder = 'images'
URL_Images = Get_Images()

async def main():
    async with aiohttp.ClientSession() as session:
        for i , URL in enumerate(URL_Images):
            await Download_Image(URL, output_folder, session)
            print("Download", i+1,"/",len(URL_Images))
            
            
asyncio.run(main())          
