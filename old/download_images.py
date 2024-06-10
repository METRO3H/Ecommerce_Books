
import json
import os
import asyncio
import aiohttp
import aiofiles
import sqlite3

async def Download_Image(image, output_folder, session):
    try:
        url = image["URL"]
        image_name = url.split('/')[-1]  # Obtiene el nombre del archivo de la URL
        image_path = os.path.join(output_folder, image_name)  # Crea la ruta completa del archivo

        async with session.get(url) as response:
            if response.status == 200:
                content = await response.read()
                if content:
                    async with aiofiles.open(image_path, mode="wb") as file:
                        await file.write(content)
                else:
                    print(f"Error: El contenido de la respuesta es None para la URL {url}")
                    return False
            else:
                print(f"Error: Fallo al descargar la imagen de {url}. Código de estado: {response.status}")
                return False

    except aiohttp.ClientError as e:
        print(f"Error de cliente HTTP al intentar descargar la imagen de {url}: {e}")
        return False
    except aiofiles.os.FileIOError as e:
        print(f"Error de E/S de archivo al intentar guardar la imagen de {url} en {image_path}: {e}")
        return False
    except Exception as e:
        print(f"Error inesperado al intentar descargar la imagen de {url}: {e}")
        return False

    return True


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
    total_rows_inserted = 0
    for image in images:
        
        book_name = image["book_name"]
        file_name = image["file_name"]
        URL = image['URL']
        product_id = image["product_id"]
        
        cursor.execute(query, (book_name, file_name, URL, product_id,))
        
        total_rows_inserted += cursor.rowcount
        
    conn.commit()
    conn.close()
    
    return total_rows_inserted

output_folder = 'images'
images = Get_Images()
missing_images = filter_images(images)
missing_images_length = len(missing_images)
message = f"There are {missing_images_length} images to download"

if missing_images == 0:
    exit
    


successful_downloads = []
failed_downloads = []
counter = 0
async def main():
    global successful_downloads, failed_downloads, counter
    async with aiohttp.ClientSession() as session:
        for image in missing_images:
            
            result = await Download_Image(image, output_folder, session)
            
            if result is False:
                failed_downloads.append(image)
                continue
            
            counter += 1
            
            print("Download", counter,"/", missing_images_length)
            
            successful_downloads.append(image)
    
            
    total_rows_inserted = insert_images(successful_downloads)        
    
    percentage = 100
    
    if missing_images_length != 0:
        percentage = round((counter/missing_images_length)*100, 1)
    
    print(percentage,"% of the images were downloaded")      
    
    print(total_rows_inserted, "covers were saved in the database")
    
    failed_downloads_json = json.dumps(failed_downloads, indent=2) 
    
    print("Missing images : ", failed_downloads_json)        
asyncio.run(main())          
