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
