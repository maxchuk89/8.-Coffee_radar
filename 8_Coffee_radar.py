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
    found_places = response.json()["response"]["GeoObjectCollection"]["featureMember"]

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant["GeoObject"]["Point"]["pos"].split(" ")
    return lat, lon


def main():
    load_dotenv()
    apikey = os.getenv("YANDEX_API_KEY")

    address = input("Где вы находитесь? ")
    user_coords = fetch_coordinates(apikey, address)

    if not user_coords:
        print("Адрес не найден.")
        return

    print("Ваши координаты:", user_coords)
    user_coords = (float(user_coords[0]), float(user_coords[1]))

    with open("coffee.json", "r", encoding="CP1251") as file:
        content = json.load(file)

    cff_shops = []
    for shop in content:
        title = shop["Name"]
        lat = shop["Latitude_WGS84"]
        lon = shop["Longitude_WGS84"]
        dist = distance(user_coords, (lat, lon)).km

        cff_shops.append(
            {"title": title, "latitude": lat, "longitude": lon, "distance": dist}
        )

    five_nearest = sorted(cff_shops, key=lambda shop: shop["distance"])[:5]

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

    print("\nПять ближайших кофеен:")
    for shop in five_nearest:
        print("-", shop["title"])

    print("\nКарта сохранена в файл map.html")


if __name__ == "__main__":
    main()
