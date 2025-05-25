import os
import requests

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
