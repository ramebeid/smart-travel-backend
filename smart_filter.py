import os
from typing import List, Dict
from datetime import datetime, timedelta
from places_utils import get_commute_time_minutes, search_google_place
from openai import OpenAI

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
    name = place.get("name", "").lower()
    keywords = ["pyramid", "eiffel", "museum", "tower", "temple", "cathedral", "ruins", "palace"]
    return any(kw in name for kw in keywords)

def ask_gpt_sentiment(reviews: List[str]) -> str:
    prompt = f"""
You are a travel review analyst. Classify the overall tone of these reviews:
{chr(10).join(reviews[:5])}

Should we recommend this place to a tourist? Answer with one word only: positive, neutral, or negative.
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip().lower()

def classify_cuisine(name: str, reviews: List[str]) -> str:
    prompt = f"""
A restaurant is called "{name}". Here are a few reviews:
{chr(10).join(reviews[:3])}

What type of cuisine does this place serve? Return a short phrase like "Lebanese grill" or "French pastries".
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

        reviews = [
            "One of my favorite places in the city!",
            "Would come again.",
            "Exceptional atmosphere and food.",
            "Family-friendly and enjoyable.",
            "Highly recommended by locals."
        ]

        if any("1 star" in r.lower() or "never again" in r.lower() for r in reviews):
            continue

        if not any("favorite" in r.lower() for r in reviews):
            sentiment = ask_gpt_sentiment(reviews)
            if sentiment != "positive":
                continue

        if "restaurant" in place.get("types", []) or "cafe" in place.get("types", []):
            place["cuisine"] = classify_cuisine(place["name"], reviews)

        filtered.append(place)

    return filtered

def prepare_final_list(city: str, places: List[Dict]) -> List[Dict]:
    must_sees = [p for p in places if is_iconic(p)]
    filtered = filter_places(places)
    return list({p["name"]: p for p in must_sees + filtered}.values())

def generate_itinerary(places: List[Dict]) -> List[Dict]:
    if not places:
        return []

    itinerary = []
    current_time = datetime.strptime("10:00", "%H:%M")
    end_time = datetime.strptime("19:00", "%H:%M")
    current_location = places[0]

    for idx, place in enumerate(places):
        if idx > 0:
            commute = get_commute_time_minutes(current_location, place)
            current_time += timedelta(minutes=commute)

        if current_time > end_time:
            break

        duration = estimate_duration(place)
        itinerary.append({
            "name": place["name"],
            "type": place.get("types", []),
            "start_time": current_time.strftime("%H:%M"),
            "duration_min": duration,
            "location": place.get("formatted_address", ""),
            "cuisine": place.get("cuisine", "")
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
