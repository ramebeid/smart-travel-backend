import os
import requests
from datetime import datetime

GOOGLE_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

def fetch_google_places(city):
    if not GOOGLE_API_KEY:
        print("❌ GOOGLE_PLACES_API_KEY not set in environment.")
        return []

    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": (
            "places.displayName,places.formattedAddress,places.rating,"
            "places.userRatingCount,places.types,places.id,places.location"
        )
    }
    payload = {
        "textQuery": f"top things to do in {city}",
        "maxResultCount": 20,
        "languageCode": "en"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            print("❌ Google Places API error:", response.text)
            return []

        data = response.json()
        raw_places = data.get("places", [])
        print(f"✅ Google returned {len(raw_places)} places for {city}")

        cleaned = []
        for p in raw_places:
            cleaned.append({
                "name": p.get("displayName", {}).get("text", ""),
                "formatted_address": p.get("formattedAddress", ""),
                "rating": p.get("rating", 0),
                "user_ratings_total": p.get("userRatingCount", 0),
                "types": p.get("types", []),
                "place_id": p.get("id")
            })

        return cleaned

    except Exception as e:
        print("❌ Exception in fetch_google_places:", str(e))
        return []

def get_reviews_for_place(place_id):
    # Placeholder for actual review scraping — simulated here
    return [
        "This was my favorite stop in the whole city!",
        "Wonderful location, highly recommend.",
        "Kids loved it, lots to do.",
        "Great local vibe and unique experience."
    ]

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
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print("Distance Matrix API error:", response.text)
            return 15

        data = response.json()
        return data["rows"][0]["elements"][0]["duration"]["value"] // 60
    except:
        return 15
