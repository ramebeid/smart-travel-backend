import os
import requests

GOOGLE_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

def fetch_google_places(city):
    url = "https://places.googleapis.com/v1/places:searchText"

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.userRatingCount"
    }

    body = {
        "textQuery": f"Top things to do in {city}",
        "maxResultCount": 20
    }

    response = requests.post(url, headers=headers, json=body)
    print("🛰 Google Places (v1) status:", response.status_code)
    print(response.text[:400])  # Optional: preview

    if response.status_code != 200:
        return []

    raw = response.json().get("places", [])
    converted = []

    for place in raw:
        converted.append({
            "name": place.get("displayName", {}).get("text", "Unknown"),
            "formatted_address": place.get("formattedAddress", ""),
            "rating": place.get("rating", 0),
            "user_ratings_total": place.get("userRatingCount", 0),
        })

    return converted


def get_commute_time_minutes(origin, destination):
    origin_address = origin.get("formatted_address")
    destination_address = destination.get("formatted_address")

    if not origin_address or not destination_address:
        return 15  # fallback

    url = (
        f"https://maps.googleapis.com/maps/api/distancematrix/json?units=metric"
        f"&origins={origin_address}&destinations={destination_address}"
        f"&key={GOOGLE_API_KEY}"
    )
    response = requests.get(url)
    if response.status_code != 200:
        print("Distance Matrix API error:", response.text)
        return 15

    try:
        return response.json()["rows"][0]["elements"][0]["duration"]["value"] // 60
    except:
        return 15
