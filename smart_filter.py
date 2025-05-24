# smart_filter.py

import re

# Must-see cultural landmarks per city
def inject_must_see_places(city):
    must_see = {
        "paris": [
            {"name": "Eiffel Tower", "rating": 4.7, "formatted_address": "Champ de Mars, 5 Av. Anatole France, 75007 Paris, France"},
            {"name": "Louvre Museum", "rating": 4.8, "formatted_address": "Rue de Rivoli, 75001 Paris, France"}
        ],
        "cairo": [
            {"name": "The Pyramids of Giza", "rating": 4.7, "formatted_address": "Al Haram, Giza Governorate, Egypt"},
            {"name": "Egyptian Museum", "rating": 4.6, "formatted_address": "Tahrir Square, Cairo, Egypt"}
        ],
        "rome": [
            {"name": "Colosseum", "rating": 4.7, "formatted_address": "Piazza del Colosseo, 1, 00184 Roma RM, Italy"},
            {"name": "Pantheon", "rating": 4.8, "formatted_address": "Piazza della Rotonda, 00186 Roma RM, Italy"}
        ]
    }
    return must_see.get(city.lower(), [])

def filter_places(places, interests, avoid_crowds=False):
    keywords = [w.lower() for w in interests]
    good = []
    for place in places:
        name = place.get("name", "").lower()
        desc = place.get("formatted_address", "").lower()
        rating = place.get("rating", 0)
        user_count = place.get("user_ratings_total", 0)
        reviews = get_reviews_for_place(place.get("place_id", ""))

        if rating < 4.6 or user_count < 10:
            continue
        if any("worst" in r.lower() or "never again" in r.lower() for r in reviews):
            continue
        if keywords and not any(k in name or k in desc for k in keywords):
            continue
        if avoid_crowds and user_count > 1000:
            continue
        if not any("favorite" in r.lower() for r in reviews):
            continue

        good.append(place)
    return good

def get_reviews_for_place(place_id):
    # Simulated for now
    return [
        "This was my favorite stop!",
        "Incredible atmosphere, loved the food!",
        "Our family had a great time, especially the kids.",
        "Would definitely return."
    ]
