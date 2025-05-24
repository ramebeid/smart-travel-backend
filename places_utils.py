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
        "textQuery": f"top attractions in {city}",
        "maxResultCount": 20
    }

    response = requests.post(url, headers=headers, json=body)
    if response.status_code != 200:
        print("❌ Google Places error:", response.text)
        return []

    raw_places = response.json().get("places", [])
    results = []
    for p in raw_places:
        results.append({
            "name": p.get("displayName", {}).get("text", "Unknown"),
            "formatted_address": p.get("formattedAddress", ""),
            "rating": p.get("rating", 0),
            "user_ratings_total": p.get("userRatingCount", 0),
        })

    return results

def get_commute_time_minutes(origin, destination):
    if not origin or not destination:
        return 10

    origin_addr = origin.get("formatted_address")
    dest_addr = destination.get("formatted_address")
    if not origin_addr or not dest_addr:
        return 10

    url = (
        f"https://maps.googleapis.com/maps/api/distancematrix/json"
        f"?origins={origin_addr}&destinations={dest_addr}&key={GOOGLE_API_KEY}"
    )

    try:
        res = requests.get(url)
        data = res.json()
        return data["rows"][0]["elements"][0]["duration"]["value"] // 60
    except:
        return 10
