import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from pathlib import Path

headers = {
    "Host": "api.axon.es",
    # "User-Agent": "",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.5",
    # "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.axon.es/",
    "content-type": "application/json",
    "authorization": "",
    # "Content-Length": "2258",
    "Origin": "https://www.axon.es",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "TE": "trailers",
}

endpoint = "https://api.axon.es/graphql"
with open(Path("scraping") / "query.graphql") as query_file:
    query = query_file.read()

variables = {
    "limit": 10,
    "skip": 0,
    # "sort": "book.edition.year",
    # "order": -1,
    # "product_type": ["book", "ebook"],
    # "lang": None,
    # "rangePrice": None,
    # "areas_of_interest": None,
    # "tags": None,
    # "type": "all",
    # "area_prox": None
}
payload = {
    "operationName": "currentProducts",
    "variables": variables,
    "query": query,
}
# payload = json.loads('{"operationName":"currentProducts","variables":{"limit":10,"skip":0,"sort":"book.edition.year","order":-1,"product_type":["book"],"lang":null,"rangePrice":null,"areas_of_interest":null,"tags":null,"type":"all","area_prox":null},"query":"query currentProducts($limit: Int, $skip: Int!, $sort: String, $order: Int, $product_type: [String], $lang: [String], $rangePrice: RangePrice, $areas_of_interest: [Int], $areas_of_interest_text: String, $tags: [TagsInput], $type: String, $searchGeneral: String, $prox: Boolean, $area_prox: String, $featured: Boolean, $is_new: Boolean) {\\n  books(\\n    limit: $limit\\n    skip: $skip\\n    sort: $sort\\n    order: $order\\n    product_type: $product_type\\n    lang: $lang\\n    rangePrice: $rangePrice\\n    areas_of_interest: $areas_of_interest\\n    areas_of_interest_text: $areas_of_interest_text\\n    tags: $tags\\n    type: $type\\n    searchGeneral: $searchGeneral\\n    prox: $prox\\n    area_prox: $area_prox\\n    featured: $featured\\n    is_new: $is_new\\n  ) {\\n    id\\n    _id\\n    titleFriendly\\n    title\\n    ean\\n    mainImg\\n    ebookContent\\n    relatedInfo {\\n      _id\\n      id\\n      product_type\\n      priceWithDiscount\\n      ean\\n      title\\n      titleFriendly\\n      ebookContent\\n      weight\\n      prices {\\n        sale\\n        clearing\\n        saleSpecialDiscount\\n        ssdFrom\\n        ssdTo\\n        __typename\\n      }\\n      book {\\n        authors {\\n          _id\\n          name\\n          __typename\\n        }\\n        pages\\n        lang\\n        binding\\n        __typename\\n      }\\n      availability {\\n        OK\\n        msg\\n        status\\n        __typename\\n      }\\n      __typename\\n    }\\n    prices {\\n      sale\\n      clearing\\n      saleSpecialDiscount\\n      ssdFrom\\n      ssdTo\\n      __typename\\n    }\\n    vat {\\n      sale\\n      __typename\\n    }\\n    tags {\\n      category\\n      items\\n      __typename\\n    }\\n    book {\\n      authors {\\n        _id\\n        name\\n        __typename\\n      }\\n      lang\\n      binding\\n      edition {\\n        year\\n        number\\n        month\\n        __typename\\n      }\\n      __typename\\n    }\\n    product_type\\n    priority\\n    priority_nov\\n    priceWithDiscount\\n    not_released\\n    __typename\\n  }\\n}\\n"}')
query_limit = 1000
# query_limit = 100
initial_skip = 0
variables["limit"] = query_limit
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
            # if query_limit == 1:
            #     break
            # else:
            #     query_limit //= 2
        else:
            # books += [book for book in result["data"]["books"] if book["stock_available"] and book["product_type"] in ["book", "ebook"]]
            books += [book for book in result["data"]["books"] if book["stock_available"] and book["product_type"] == "book"]
            print(f"Saving {len(books)} so far")
            accumulated_skip += query_limit
            # tmp:
            with open("libros.json", "w") as file:
                json.dump(books, file)
        i += 1

    with open("libros.json", "w") as file:
        json.dump(books, file)
except HTTPError as http_error:
    if http_error.code != 400:
        raise http_error
    errors = json.loads(http_error.read())["errors"]
    for error in errors:
        print(error["message"])
