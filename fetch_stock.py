import json
from urllib.request import Request, urlopen
import sys

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
query = '''
  query currentProducts($limit: Int, $skip: Int!, $sort: String, $order: Int, $product_type: [String], $lang: [String], $rangePrice: RangePrice, $areas_of_interest: [Int], $areas_of_interest_text: String, $tags: [TagsInput], $type: String, $searchGeneral: String, $prox: Boolean, $area_prox: String, $featured: Boolean, $is_new: Boolean, $id: Int) {
    books(
      limit: $limit
      skip: $skip
      sort: $sort
      order: $order
      product_type: $product_type
      lang: $lang
      rangePrice: $rangePrice
      areas_of_interest: $areas_of_interest
      areas_of_interest_text: $areas_of_interest_text
      tags: $tags
      type: $type
      searchGeneral: $searchGeneral
      prox: $prox
      area_prox: $area_prox
      featured: $featured
      is_new: $is_new
      id: $id
    ) {
      id
      titleFriendly
      stock_available
    }
  }
'''

if len(sys.argv) < 3:
    print(f"Uso: {sys.argv[0]} <id> <titleFriendly>")
    sys.exit(1)

id = int(sys.argv[1])
name_query = sys.argv[2]
variables = {
    "limit": 100,
    "skip": 0,
    # "id": 8669,
    "searchGeneral": name_query,
    "sort": "book.edition.year",
    "order": -1,
    "lang": None,
    "rangePrice": None,
    "areas_of_interest": None,
    "tags": None,
    "type": "all",
    "area_prox": None
}
payload = {
    "operationName": "currentProducts",
    "variables": variables,
    "query": query,
}
request = Request(endpoint, data=json.dumps(payload, separators=(",", ":")).encode(), headers=headers)
with urlopen(request) as response:
    result = json.loads(response.read())

for book in result["data"]["books"]:
    # name_query isn't necessary but just in case
    if book["id"] == id and book["titleFriendly"] == name_query:
        print(book["stock_available"])
        break
