import os
import requests

GOOGLE_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

def search_google_place(name):
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating,places.userRatingCount,places.id"
    }
    payload = {"textQuery": name, "maxResultCount": 1, "languageCode": "en"}

    res = requests.post(url, headers=headers, json=payload)
    if res.status_code != 200:
        print("Google Place Search Error:", res.text)
        return None

    places = res.json().get("places", [])
    return places[0] if places else None

def has_acceptable_reviews(place):
    rating = place.get("rating", 0)
    if rating < 4.6:
        return False

    reviews = get_reviews_for_place(place["id"])
    return not any("1 star" in r.lower() or "never again" in r.lower() for r in reviews)

def get_reviews_for_place(place_id):
    return [
        "Absolutely loved it!",
        "Amazing spot, would go again.",
        "Best local food, great vibe!",
        "My favorite place on the trip."
    ]
