import os
import requests

GOOGLE_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")

def fetch_google_places(city):
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query=things+to+do+in+{city}&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Google Places API error:", response.text)
        return []
    return response.json().get("results", [])

def get_reviews_for_place(place_id):
    url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=reviews&key={GOOGLE_API_KEY}"
    response = requests.get(url)
    if response.status_code != 200:
        print("Details API error:", response.text)
        return []

    data = response.json()
    all_reviews = data.get("result", {}).get("reviews", [])
    one_month_ago = datetime.utcnow().timestamp() - (30 * 86400)

    recent_reviews = []
    for review in all_reviews:
        time = review.get("time", 0)
        if time >= one_month_ago:
            recent_reviews.append(review.get("text", ""))

    return recent_reviews


def get_commute_time_minutes(origin, destination):
    origin_address = origin.get("formatted_address")
    destination_address = destination.get("formatted_address")

    if not origin_address or not destination_address:
        return 15

    url = (
        f"https://maps.googleapis.com/maps/api/distancematrix/json?units=metric"
        f"&origins={origin_address}&destinations={destination_address}"
        f"&key={GOOGLE_API_KEY}"
    )
    response = requests.get(url)
    if response.status_code != 200:
        print("Distance Matrix API error:", response.text)
        return 15

    data = response.json()
    try:
        return data["rows"][0]["elements"][0]["duration"]["value"] // 60
    except:
        return 15
