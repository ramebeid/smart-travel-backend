# smart_filter.py

import re
from places_utils import fetch_google_places

def inject_must_see_places(city):
    all_places = fetch_google_places(city)
    must_keywords = ["museum", "monument", "castle", "cathedral", "temple", "palace", "pyramids", "landmark", "heritage", "historic"]
    must_see = []

    for place in all_places:
        name = place.get("name", "").lower()
        desc = place.get("formatted_address", "").lower()
        if any(k in name or k in desc for k in must_keywords):
            must_see.append(place)

    return must_see[:4]  # prioritize top 4 culturally important

def filter_places(places, interests, avoid_crowds=False):
    keywords = [kw.strip().lower() for kw in interests if kw.strip()]
    good = []

    for place in places:
        name = place.get("name", "").lower()
        desc = place.get("formatted_address", "").lower()
        rating = place.get("rating", 0)
        user_count = place.get("user_ratings_total", 0)
        reviews = get_reviews_for_place(place.get("place_id", ""))

        if rating < 4.6:
            continue
        if any(bad in r.lower() for r in reviews for bad in ["worst", "never again", "horrible", "disgusting"]):
            continue
        if avoid_crowds and user_count > 1200:
            continue
        if not avoid_crowds and user_count < 10:
            continue
        if keywords and not any(k in name or k in desc for k in keywords):
            continue

        good.append(place)

    if not good:
        sorted_places = sorted(places, key=lambda x: x.get("rating", 0), reverse=True)
        good = sorted_places[:5]

    print(f"✅ Filtered down to {len(good)} places")
    return good

def get_reviews_for_place(place_id):
    # Placeholder until we use real review API (scraping not feasible)
    return [
        "Amazing visit!",
        "Highly recommended",
        "My favorite stop in the whole trip",
        "Will return again"
    ]
