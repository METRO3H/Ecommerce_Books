import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from pathlib import Path

headers = {
    "Host": "api.axon.es",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    # "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.axon.es/",
    "content-type": "application/json",
    "authorization": "",
    "Origin": "https://www.axon.es",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "TE": "trailers",
}

endpoint = "https://api.axon.es/graphql"

def scrape(query_limit=1000):
    with open(Path("scraping") / "query.graphql") as query_file:
        query = query_file.read()
    variables = {
        "limit": query_limit,
        "skip": 0,
    }
    payload = {
        "operationName": "currentProducts",
        "variables": variables,
        "query": query,
    }
    initial_skip = 0
    books = []
    i = 0
    accumulated_skip = 0
    try:
        while True:
            print(f"Iteration {i}")
            print(f"{query_limit = }")
            variables["skip"] = initial_skip + accumulated_skip
            request = Request(endpoint, data=json.dumps(payload, separators=(",", ":")).encode(), headers=headers)
            with urlopen(request) as response:
                result = json.loads(response.read())
            if not result["data"]["books"]:
                break
            else:
                books += [book for book in result["data"]["books"] if book["stock_available"] and book["product_type"] == "book"]
                print(f"Saving {len(books)} so far")
                accumulated_skip += query_limit
            i += 1

        with open("libros.json", "w") as file:
            json.dump(books, file)
    except HTTPError as http_error:
        if http_error.code != 400:
            raise http_error
        errors = json.loads(http_error.read())["errors"]
        for error in errors:
            print(error["message"])

if __name__ == "__main__":
    scrape()
