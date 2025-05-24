# smart_filter.py

import re

# Automatically inject cultural must-see places using keywords

def inject_must_see_places(city):
    from places_utils import fetch_google_places
    all_places = fetch_google_places(city)
    must_keywords = ["museum", "monument", "castle", "cathedral", "temple", "palace", "pyramids"]
    must_see = []
    for place in all_places:
        name = place.get("name", "").lower()
        desc = place.get("formatted_address", "").lower()
        if any(k in name or k in desc for k in must_keywords):
            must_see.append(place)
    return must_see[:4]

def filter_places(places, interests, avoid_crowds=False):
    keywords = [w.lower() for w in interests if w.strip()]
    good = []

    for place in places:
        name = place.get("name", "").lower()
        desc = place.get("formatted_address", "").lower()
        rating = place.get("rating", 0)
        user_count = place.get("user_ratings_total", 0)
        reviews = get_reviews_for_place(place.get("place_id", ""))

        if rating < 4.2:
            continue
        if not avoid_crowds and user_count < 10:
            continue
        if avoid_crowds and user_count > 1200:
            continue
        if any("worst" in r.lower() or "never again" in r.lower() for r in reviews):
            continue

        # Apply interest filter only if provided
        if keywords and not any(k in name or k in desc for k in keywords):
            continue

        good.append(place)

    if not good and not keywords:
        # fallback to top 5 rated if everything is filtered out
        sorted_places = sorted(places, key=lambda x: x.get("rating", 0), reverse=True)
        good = sorted_places[:5]

    print(f"✅ Filtered down to {len(good)} places out of {len(places)}")
    return good

def get_reviews_for_place(place_id):
    return [
        "This was my favorite stop!",
        "Incredible atmosphere, loved the food!",
        "Our family had a great time, especially the kids.",
        "Would definitely return."
    ]
