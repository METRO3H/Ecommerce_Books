
import aiohttp
import json
import os
from .get_images import Get_Images
from .filter_images import filter_images
from .download_image import Download_Image
from .insert_images_db import insert_images

async def Process_Covers():
    output_folder = 'images'

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    images = Get_Images()
    # missing_images = filter_images(images)
    # missing_images_length = len(missing_images)
    # print(missing_images)
    # if missing_images_length == 0:
    #     print(f"There are {missing_images_length} missing images to download")
    #     return

    successful_downloads = []
    failed_downloads = []
    percentage = 0

    async with aiohttp.ClientSession() as session:
        for image in images:
            # print(image["book_name"])
            result = await Download_Image(image, output_folder, session)
            if result is False:
                failed_downloads.append(image)
                continue


            successful_downloads.append(image)

            percentage = round((len(successful_downloads)/len(images))*100, 2)
            percentage = int(percentage) if percentage.is_integer() else percentage
            ratio = f"{len(successful_downloads)}/{len(images)}"
            print(f"Download {ratio} - {percentage}% : {image['book_name']}")

    print(f"{percentage}% of the images were downloaded!")

    if len(failed_downloads) != 0:

        print(len(failed_downloads), "Failed downloads : \n")

        for image in failed_downloads:
            print(f"-> {image['product_id']} - {image['book_name']} - {image['URL']}")

    # total_rows_inserted = insert_images(successful_downloads)

    # if total_rows_inserted == 1:
    #     print("A cover was saved in the database")
    # else:
    #     print(f"{total_rows_inserted} covers were saved in the database")



