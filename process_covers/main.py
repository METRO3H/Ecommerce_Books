
import aiohttp
import json

from .get_images import Get_Images
from .filter_images import filter_images
from .download_image import Download_Image
from .insert_images_db import insert_images

async def Process_Covers():
    output_folder = 'images'
    images = Get_Images()
    missing_images = filter_images(images)
    missing_images_length = len(missing_images)

    if missing_images_length == 0:
        print(f"There are {missing_images_length} missing images to download")
        exit()

    successful_downloads = []
    failed_downloads = []
    
    async with aiohttp.ClientSession() as session:
        for image in missing_images:
            result = await Download_Image(image, output_folder, session)
            if result is False:
                failed_downloads.append(image)
                continue
            
            print(f"Download {len(successful_downloads) + 1}/{missing_images_length}")
            successful_downloads.append(image)
    
    total_rows_inserted = insert_images(successful_downloads)        
    
    percentage = 100
    if missing_images_length != 0:
        percentage = round((len(successful_downloads)/missing_images_length)*100, 1)
    
    print(f"{percentage}% of the images were downloaded")      
    print(f"{total_rows_inserted} covers were saved in the database")
    
    failed_downloads_json = json.dumps(failed_downloads, indent=2)     
    print("Missing images : ", failed_downloads_json)        
    
