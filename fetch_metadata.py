import json
from urllib.request import urlopen
from bs4 import BeautifulSoup

with open("libros.json") as file:
    books = json.load(file)

url_prefix = "https://www.axon.es/ficha/libros"
for book in books:
    url = f"{url_prefix}/{book['ean']}/{book['titleFriendly']}"
    with urlopen(url) as response:
        soup = BeautifulSoup(response, "html.parser")
    breakpoint()
