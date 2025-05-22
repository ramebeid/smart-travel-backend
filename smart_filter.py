# smart_filter.py

from typing import List, Dict
import openai
from places_utils import get_reviews_for_place

# Assume OPENAI_API_KEY is loaded from .env elsewhere
openai.api_key = os.getenv("OPENAI_API_KEY")

# ---------- Main Smart Filter Logic ----------
def filter_places(places: List[Dict]) -> List[Dict]:
    filtered = []
    for place in places:
        rating = place.get("rating", 0)
        reviews_count = place.get("user_ratings_total", 0)

        # 1. Filter out bad places
        if rating <= 1.0 or reviews_count == 0:
            continue

        # 2. Pull recent reviews and run GPT sentiment check
        reviews = get_reviews_for_place(place["place_id"])
        if not reviews:
            continue

        favorite_found = any("favorite" in r.lower() for r in reviews)
        if not favorite_found:
            # Ask GPT if it's worth recommending
            sentiment = ask_gpt_sentiment(reviews)
            if sentiment != "positive":
                continue

        # 3. Check for family/kids-friendly tags
        is_for_kids = any(tag in place.get("types", []) for tag in ["amusement_park", "zoo", "playground"])
        place["kids_friendly"] = is_for_kids

        # 4. Add cuisine type using GPT if restaurant
        if "restaurant" in place.get("types", []):
            cuisine_type = classify_cuisine(place["name"], reviews)
            place["cuisine"] = cuisine_type

        filtered.append(place)

    return filtered


# ---------- GPT Classifiers ----------
def ask_gpt_sentiment(reviews: List[str]) -> str:
    joined = "\n".join(reviews[:5])
    prompt = f"""
    You are an expert travel assistant. Classify the overall tone of these reviews:
    """
    {joined}
    """
    Is this place a good recommendation for a tourist? Answer only: positive, neutral, or negative.
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"].strip().lower()


def classify_cuisine(name: str, reviews: List[str]) -> str:
    joined = "\n".join(reviews[:3])
    prompt = f"""
    A restaurant is called "{name}". Here are a few recent reviews:
    """
    {joined}
    """
    What type of cuisine does this restaurant serve? Return a short answer like "Egyptian street food" or "Italian pasta restaurant".
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response["choices"][0]["message"]["content"].strip()


# ---------- Bonus: Ensure Cultural Sites Always Included ----------
def inject_must_see_places(city: str, existing: List[Dict]) -> List[Dict]:
    must_see_map = {
        "cairo": ["Egyptian Museum", "Pyramids of Giza", "Khan El-Khalili"],
        "paris": ["Eiffel Tower", "Louvre Museum", "Notre Dame"]
    }
    required = must_see_map.get(city.lower(), [])
    names = [p["name"] for p in existing]

    for place in required:
        if place not in names:
            existing.append({"name": place, "priority": "must-see"})

    return existing
