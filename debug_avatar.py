from avatar_assets import get_avatar_url

config = {
    "top": "shortHair",
    "hairColor": "2c1b18", # Black
    "skinColor": "edb98a",
    "clothing": "hoodie",
    "eyes": "happy",
    "eyebrows": "default",
    "mouth": "smile",
    "accessories": "prescription01"
}

url = get_avatar_url(config)
print(f"URL: {url}")

config["top"] = "longHair"
url2 = get_avatar_url(config)
print(f"URL2: {url2}")
