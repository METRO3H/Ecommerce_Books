import pandas as pd
import json
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

df = pd.read_csv("data.csv")
important_keys = list(df.dropna(axis="columns", how="all").columns)
dfi = df[important_keys]
non_redundant_keys = [x for x in important_keys if len(dfi[x].value_counts()) > 1]
dfii = dfi[non_redundant_keys]

print("Loading libros.json")
with open("libros.json") as file:
    libros = json.load(file)

print("Processing libros.json")
libros_df = pd.json_normalize(libros)
libros_df = libros_df.loc[(libros_df["product_type"] == "book")]
libros_df = libros_df.loc[(libros_df["stock_available"] > 0)]
# Tags are useless
# tags_df = pd.json_normalize(libros_df.explode("tags")["tags"]).rename(lambda x: "tags." + x, axis="columns")
# libros_df = libros_df.join(tags_df)
libros_df.loc[libros_df["prices.sale"] == libros_df["priceWithDiscount"], "prices.sale"]["prices.sale"] = None
libros_df = libros_df.rename(
    {
        "id": "ID",
        "title": "Name",
        "book.description": "Description",
        "priceWithDiscount": "Sale price?",
        "prices.sale": "Regular price",
        "product_type": "Categories",
        "mainImg": "Images",
    },
    axis="columns"
)

fmt = "http://bookstore.local/wp-content/uploads/2024/05{}"
libros_df["Images"] = libros_df["Images"].map(lambda x: fmt.format(urlsplit(x)[2]))

libros_df["In stock?"] = libros_df["stock_available"].astype(bool).astype(int)
libros_df["Published"] = 1

libros_df["Description"] = libros_df["Description"].map(lambda x: None if x is None else BeautifulSoup(x, "html.parser").get_text("\n", True))

print("Making dataframe similar to default one")
# Add all keys not in libros_df which in original are all with the same value to libros_df
repeated_keys = [x for x in df.columns if x not in libros_df and (df[x][0] == df[x]).all()]
for x in repeated_keys:
    libros_df[x] = df[x][0]

# Drop all keys in libros_df that are not in original
trash_keys = [x for x in libros_df.columns if x not in df]
libros_df = libros_df.drop(trash_keys, axis="columns")

# libros_df["Description"] = libros_df["Short description"] = libros_df["Name"] = "-"
# libros_df["Images"] = df["Images"][0]
# Add missing keys from original as nan
missing_keys = [x for x in df.columns if x not in libros_df]
for x in missing_keys:
    libros_df[x] = df[x][0]
    # libros_df[x] = None

# Reorder columns to fit original order
libros_df = libros_df[df.columns]

libros_df = libros_df.reset_index(drop=True)

# print("Filtering down to 100 chosen elements")
# Temporary, 100 random books chosen
# choices = [2563, 1546, 1035, 5140, 3095, 29, 3104, 3631, 3123, 56, 2107, 3656, 2636, 3160, 4699, 2658, 2166, 1145, 123, 3213, 1173, 3222, 1690, 1186, 4775, 699, 1723, 4797, 706, 4297, 3795, 1240, 3289, 732, 4830, 2796, 4340, 3830, 251, 3326, 1279, 2816, 268, 1807, 1297, 294, 3884, 300, 3888, 3378, 1846, 823, 4924, 318, 321, 4425, 3404, 3920, 4947, 854, 3416, 2413, 3443, 372, 893, 2434, 2947, 1410, 3461, 389, 3983, 1425, 3485, 1437, 4004, 5043, 4020, 1467, 1983, 3015, 1483, 978, 4058, 475, 5084, 2527, 4063, 993, 5089, 3044, 3564, 2543, 495, 1010, 5109, 3576, 2553, 2554, 1532, 4093]
# libros_df = libros_df.loc[choices].reset_index(drop=True)

print("Exporting to output.csv")
libros_df.to_csv("output.csv", index=False)
