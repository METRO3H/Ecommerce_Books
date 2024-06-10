
import json
import os
import asyncio
import aiohttp
import aiofiles
import sqlite3

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

    images = []

    # Iterar sobre cada item en tus datos
    for item in data:
        # Verificar si 'mainImg' está presente en el item
        if 'mainImg' in item and item["product_type"] == "book" and item["stock_available"]:
            
            image_url = item['mainImg']
            book_name = item["titleFriendly"]
            product_id = item["id"]
            
            if image_url is None:
                print(product_id, " - ", book_name, " - ", image_url)
                none_counter += 1
                continue
            

            images.append({
                "book_name" : book_name,
                "file_name" : image_url.split("/")[-1],
                "URL" : image_url,
                "product_id" : product_id
            })
            
    print("None : ", none_counter)
    
    return images

#LE FALTA
def filter_images(images):
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    query = """
    --sql
    SELECT book_name, file_name, url, product_id FROM covers
    ;
    """
    cursor.execute(query)
    saved_images = cursor.fetchall()
    
    conn.close()
    
    columns = [description[0] for description in cursor.description]
    
    saved_images_dictionary = []
    
    for saved_image in saved_images:
        dict_row = dict(zip(columns, saved_image))
        saved_images_dictionary.append(dict_row)

    # for i in range(10):
    #     print("Images : ", json.dumps(images[i], indent=2))
    #     print("Saved images : ", json.dumps(saved_images_dictionary[i], indent=2))
        
    # missing_images = [item for item in images if item not in saved_images_dictionary]
    
    saved_product_ids = {item['product_id'] for item in saved_images_dictionary}
    
    missing_images  = [item for item in images if item['product_id'] not in saved_product_ids]
    
    return missing_images

def insert_images(images):
    conn = sqlite3.connect('database/database.db')
    cursor = conn.cursor()
    query = """
    --sql
    INSERT INTO covers (book_name, file_name, url, product_id) 
    VALUES (?, ?, ?, ?)
    ;
    """
    
    for image in images:
        
        book_name = image["book_name"]
        file_name = image["file_name"]
        URL = image['URL']
        product_id = image["product_id"]
        
        cursor.execute(query, (book_name, file_name, URL, product_id,))

    conn.commit()
    conn.close()
    
    return

output_folder = 'images'
images = Get_Images()
missing_images = filter_images(images)
missing_images_length = len(missing_images)
message = f"There are {missing_images_length} images to download"

if missing_images == 0:
    exit
    
insert_images(images)

successful_downloads = []
failed_downloads = []
async def main():
    async with aiohttp.ClientSession() as session:
        for i , image in enumerate(missing_images):
            await Download_Image(image["URL"], output_folder, session)
            print("Download", i+1,"/",len(missing_images))
            
            
asyncio.run(main())          
