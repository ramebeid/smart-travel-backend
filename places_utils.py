import os
import requests

GOOGLE_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

def search_google_place(city):
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.types,places.id"
    }
    payload = {
        "textQuery": f"top things to do in {city}",
        "maxResultCount": 20,
        "languageCode": "en"
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code != 200:
        print("Google API error:", response.text)
        return []

    places = []
    for p in response.json().get("places", []):
        places.append({
            "name": p.get("displayName", {}).get("text", ""),
            "formatted_address": p.get("formattedAddress", ""),
            "rating": p.get("rating", 0),
            "user_ratings_total": p.get("userRatingCount", 0),
            "types": p.get("types", []),
            "place_id": p.get("id", "")
        })

    return places

def get_commute_time_minutes(origin, destination):
    # NOTE: This is a simplified version. You can expand with real distance matrix API if needed.
    return 20  # fixed estimate for MVP
