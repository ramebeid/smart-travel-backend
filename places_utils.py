import os
import requests

GOOGLE_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

def get_place_details(name):
    search_url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": name, "key": GOOGLE_API_KEY}
    search_response = requests.get(search_url, params=params)

    if search_response.status_code != 200:
        return None

    results = search_response.json().get("results", [])
    if not results:
        return None

    place = results[0]
    place_id = place.get("place_id")

    details_url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {"place_id": place_id, "key": GOOGLE_API_KEY}
    details_response = requests.get(details_url, params=params)

    if details_response.status_code != 200:
        return None

    detail_result = details_response.json().get("result", {})
    reviews = detail_result.get("reviews", [])

    return {
        "address": detail_result.get("formatted_address"),
        "rating": detail_result.get("rating", 0),
        "reviews": reviews
    }

def get_commute_time_minutes(origin_name, destination_name):
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": origin_name,
        "destinations": destination_name,
        "key": GOOGLE_API_KEY,
        "units": "metric"
    }
    response = requests.get(url, params=params)

    try:
        data = response.json()
        return data["rows"][0]["elements"][0]["duration"]["value"] // 60
    except:
        return 15
