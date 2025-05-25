import os
from datetime import datetime, timedelta
from typing import List, Dict
from openai import OpenAI
from places_utils import get_reviews_for_place, get_commute_time_minutes

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

VISIT_DURATION = {
    "museum": 120,
    "tourist_attraction": 90,
    "park": 45,
    "restaurant": 75,
    "cafe": 30,
    "zoo": 90,
    "shopping_mall": 60,
    "playground": 45
}

def is_iconic(place):
    name = place["name"].lower()
    keywords = ["pyramid", "eiffel", "museum", "tower", "temple", "cathedral", "ruins", "palace"]
    return any(k in name for k in keywords)

def ask_gpt_sentiment(reviews: List[str]) -> str:
    prompt = f"""
    You are an expert travel assistant. Classify the overall tone of these reviews:
    {"".join(reviews[:5])}
    Is this place a good recommendation for a tourist? Answer only: positive, neutral, or negative.
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip().lower()

def classify_cuisine(name: str, reviews: List[str]) -> str:
    prompt = f"""
    A restaurant is called "{name}". Here are a few recent reviews:
    {"".join(reviews[:3])}
    What type of cuisine does this restaurant serve? Return a short answer like "Egyptian street food" or "Italian pasta restaurant".
    """
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def filter_places(places: List[Dict]) -> List[Dict]:
    filtered = []
    for place in places:
        rating = place.get("rating", 0)
        reviews_count = place.get("user_ratings_total", 0)

        if rating < 4.6 or reviews_count == 0:
            continue

        reviews = get_reviews_for_place(place["place_id"])
        if not reviews:
            continue

        if any("1 star" in r.lower() or "terrible" in r.lower() or "never again" in r.lower() for r in reviews):
            continue

        favorite_found = any("favorite" in r.lower() for r in reviews)
        if not favorite_found:
            sentiment = ask_gpt_sentiment(reviews)
            if sentiment != "positive":
                continue

        if "restaurant" in place.get("types", []) or "cafe" in place.get("types", []):
            place["cuisine"] = classify_cuisine(place["name"], reviews)

        filtered.append(place)

    return filtered

def prepare_final_list(city: str, all_places: List[Dict]) -> List[Dict]:
    must_sees = [p for p in all_places if is_iconic(p)]
    hidden_gems = filter_places(all_places)
    combined = list({p["name"]: p for p in (must_sees + hidden_gems)}.values())
    return combined

def generate_itinerary(places: List[Dict]) -> List[Dict]:
    if not places:
        return []

    itinerary = []
    current_time = datetime.strptime("10:00", "%H:%M")
    end_time = datetime.strptime("19:00", "%H:%M")
    current_location = places[0]

    for idx, place in enumerate(places):
        if idx > 0:
            commute_minutes = get_commute_time_minutes(current_location, place)
            current_time += timedelta(minutes=commute_minutes)

        if current_time > end_time:
            break

        duration = estimate_duration(place)
        itinerary.append({
            "name": place["name"],
            "type": place.get("types", []),
            "cuisine": place.get("cuisine", ""),
            "start_time": current_time.strftime("%H:%M"),
            "duration_min": duration,
            "location": place.get("formatted_address", "")
        })

        current_time += timedelta(minutes=duration)
        current_location = place

    return itinerary

def estimate_duration(place):
    types = place.get("types", [])
    for t in types:
        if t in VISIT_DURATION:
            return VISIT_DURATION[t]
    return 60
