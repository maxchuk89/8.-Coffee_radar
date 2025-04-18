import os
import json

import requests
import folium
from geopy.distance import distance
from dotenv import load_dotenv


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(
        base_url,
        params={"geocode": address, "apikey": apikey, "format": "json"},
    )
    response.raise_for_status()
    lon, lat = (
        response.json()["response"]["GeoObjectCollection"]["featureMember"][0]
        ["GeoObject"]["Point"]["pos"]
        .split(" ")
    )
    return lat, lon


def main():
    load_dotenv()
    apikey = os.getenv("YANDEX_API_KEY")

    address = input("Где вы находитесь? ")
    user_coords = fetch_coordinates(apikey, address)
    user_coords = float(user_coords[0]), float(user_coords[1])

    with open("coffee.json", "r", encoding="CP1251") as file:
        content = json.load(file)

    cff_shops = []
    for shop in content:
        dist = distance(
            user_coords,
            (shop["Latitude_WGS84"], shop["Longitude_WGS84"]),
        ).km
        cff_shops.append(
            {
                "title": shop["Name"],
                "latitude": shop["Latitude_WGS84"],
                "longitude": shop["Longitude_WGS84"],
                "distance": dist,
            }
        )

    five_nearest = sorted(cff_shops, key=lambda s: s["distance"])[:5]

    map_object = folium.Map(location=user_coords, zoom_start=14)
    folium.Marker(location=user_coords, icon=folium.Icon(color="red")).add_to(
        map_object
    )
    for shop in five_nearest:
        folium.Marker(
            location=[float(shop["latitude"]), float(shop["longitude"])],
            icon=folium.Icon(color="green", icon="coffee", prefix="fa"),
        ).add_to(map_object)

    map_object.save("map.html")


if __name__ == "__main__":
    main()