def fix_payload [] {
	$in | to json -r | str replace -a '": ' '":'
}

def gen_payload [query] {
	{query: $query} | fix_payload
}

let headers = [Host, api.axon.es, User-Agent, "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0", Accept, */*, Accept-Language, "en-US,en;q=0.5", Accept-Encoding, "gzip, deflate, br", Referer, "https://www.axon.es/", content-type, application/json, authorization, "", Origin, "https://www.axon.es", Connection, keep-alive, Sec-Fetch-Dest, empty, Sec-Fetch-Mode, cors, Sec-Fetch-Site, same-site, TE, trailers]

def fetch_payload [payload] {
	http post --headers $headers 'https://api.axon.es/graphql' $payload | get data
}

def fetch_query [query] {
	fetch_payload (gen_payload $query)
}

let copied_payload = '{"operationName":"currentProducts","variables":{"limit":10,"skip":0,"sort":"book.edition.year","order":-1,"product_type":["book"],"lang":null,"rangePrice":null,"areas_of_interest":null,"tags":null,"type":"all","area_prox":null},"query":"query currentProducts($limit: Int, $skip: Int!, $sort: String, $order: Int, $product_type: [String], $lang: [String], $rangePrice: RangePrice, $areas_of_interest: [Int], $areas_of_interest_text: String, $tags: [TagsInput], $type: String, $searchGeneral: String, $prox: Boolean, $area_prox: String, $featured: Boolean, $is_new: Boolean) {\n  books(\n    limit: $limit\n    skip: $skip\n    sort: $sort\n    order: $order\n    product_type: $product_type\n    lang: $lang\n    rangePrice: $rangePrice\n    areas_of_interest: $areas_of_interest\n    areas_of_interest_text: $areas_of_interest_text\n    tags: $tags\n    type: $type\n    searchGeneral: $searchGeneral\n    prox: $prox\n    area_prox: $area_prox\n    featured: $featured\n    is_new: $is_new\n  ) {\n    id\n    _id\n    titleFriendly\n    title\n    ean\n    mainImg\n    ebookContent\n    relatedInfo {\n      _id\n      id\n      product_type\n      priceWithDiscount\n      ean\n      title\n      titleFriendly\n      ebookContent\n      weight\n      prices {\n        sale\n        clearing\n        saleSpecialDiscount\n        ssdFrom\n        ssdTo\n        __typename\n      }\n      book {\n        authors {\n          _id\n          name\n          __typename\n        }\n        pages\n        lang\n        binding\n        __typename\n      }\n      availability {\n        OK\n        msg\n        status\n        __typename\n      }\n      __typename\n    }\n    prices {\n      sale\n      clearing\n      saleSpecialDiscount\n      ssdFrom\n      ssdTo\n      __typename\n    }\n    vat {\n      sale\n      __typename\n    }\n    tags {\n      category\n      items\n      __typename\n    }\n    book {\n      authors {\n        _id\n        name\n        __typename\n      }\n      lang\n      binding\n      edition {\n        year\n        number\n        month\n        __typename\n      }\n      __typename\n    }\n    product_type\n    priority\n    priority_nov\n    priceWithDiscount\n    not_released\n    __typename\n  }\n}\n"}'

let fields = fetch_query '{__type(name: "RootQuery") { fields {name} } }' | get __type.fields

let books_args = fetch_query '{ __type(name: "RootQuery") {fields { name args { name defaultValue type { name } } } }}' | get __type.fields | where name == books | flatten | flatten | flatten
