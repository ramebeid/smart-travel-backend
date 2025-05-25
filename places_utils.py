# places_utils.py

import os
import requests

GOOGLE_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

def fetch_google_places(city):
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.types,places.id,places.location"
    }
    payload = {
        "textQuery": f"top things to do in {city}",
        "maxResultCount": 20,
        "languageCode": "en"
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 200:
        print("Google Places API error:", response.text)
        return []

    places = response.json().get("places", [])
    results = []
    for p in places:
        results.append({
            "name": p.get("displayName", {}).get("text"),
            "formatted_address": p.get("formattedAddress"),
            "rating": p.get("rating"),
            "user_ratings_total": p.get("userRatingCount"),
            "types": p.get("types", []),
            "place_id": p.get("id"),
        })

    return results

def get_reviews_for_place(place_id):
    return [
        "Amazing place, totally worth it.",
        "One of my favorite stops of the trip!",
        "Very family friendly, the kids loved it.",
        "Would absolutely come again."
    ]

def get_commute_time_minutes(origin, destination):
    return 15  # Dummy fallback. Replace later with real Distance Matrix logic if needed.
