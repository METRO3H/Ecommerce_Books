
import aiohttp
import aiofiles
import os

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
