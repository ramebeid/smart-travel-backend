import os
import requests

def fetch_google_places(city, interests):
    api_key = os.getenv("GOOGLE_PLACES_API_KEY")
    if not api_key:
        print("❌ GOOGLE_PLACES_API_KEY not set.")
        return []

    results = []

    for interest in interests:
        query = f"{interest} in {city}"
        url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={query}&key={api_key}"
        response = requests.get(url)
        data = response.json()

        if "results" in data:
            for place in data["results"]:
                name = place.get("name", "")
                rating = place.get("rating", 0)
                user_ratings_total = place.get("user_ratings_total", 0)
                place_id = place.get("place_id", "")
                open_now = place.get("opening_hours", {}).get("open_now", False)

                if rating >= 4.6 and user_ratings_total >= 30:
                    maps_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}"
                    status = "Open Now" if open_now else "Closed"
                    formatted = f"{name} | {rating}★ | {user_ratings_total} reviews | {status} | {maps_url}"
                    results.append(formatted)

    print(f"[Google Places] Returning {len(results)} places for {city}")
    return results

    # TEMPORARY MOCK until review scraping is added
def get_reviews_for_place(place_id):
    return [
        "This is my favorite place ever!",
        "Amazing experience, will return again.",
        "Great for kids and families.",
        "Tasty food, excellent local flavors."
    ]
