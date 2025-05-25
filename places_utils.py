import os
import requests

GOOGLE_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

def search_google_place(text, city):
    url = "https://places.googleapis.com/v1/places:searchText"
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_API_KEY,
        "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.rating"
    }
    payload = {
        "textQuery": f"{text} in {city}",
        "maxResultCount": 1,
        "languageCode": "en"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            return None

        places = response.json().get("places", [])
        if not places:
            return None

        p = places[0]
        name = p.get("displayName", {}).get("text", "")
        address = p.get("formattedAddress", "")
        rating = p.get("rating", "N/A")

        return f"{name}, {address}, {rating}★"
    except:
        return None
